/* Headless libmgba driver for QA screenshots / interaction repro (HLE BIOS, no BIOS file).
 * usage: mgba_shot ROM SCRIPT
 * script lines:  wait N | hold KEYS N | shot FILE.ppm | peek16 ADDR | watch N | # comment
 *   watch N: single-step up to N frames; when execution jumps back to the reset
 *            vector / ROM entry (a crash that reboots, e.g. a NULL call) print
 *            the last 64 PCs + LR so the bad branch can be traced
 * KEYS = '+'-joined A,B,SELECT,START,RIGHT,LEFT,UP,DOWN,R,L  */
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/log.h>
#include <mgba/internal/arm/arm.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void nolog(struct mLogger* l, int c, enum mLogLevel lv, const char* f, va_list a) { (void)l;(void)c;(void)lv;(void)f;(void)a; }
static struct mLogger L = { .log = nolog };
static unsigned W, H; static color_t* buf; static struct mCore* core;
static void frames(int n, uint32_t keys) { core->setKeys(core, keys); for (int i = 0; i < n; i++) core->runFrame(core); }
static uint32_t parsekeys(char* s) {
	static const char* names[] = {"A","B","SELECT","START","RIGHT","LEFT","UP","DOWN","R","L"};
	uint32_t k = 0; for (char* t = strtok(s, "+"); t; t = strtok(NULL, "+"))
		for (int i = 0; i < 10; i++) if (!strcmp(t, names[i])) k |= 1u << i;
	return k;
}
static void shot(const char* path) {
	FILE* f = fopen(path, "wb"); fprintf(f, "P6\n%u %u\n255\n", W, H);
	for (unsigned i = 0; i < W * H; i++) { uint32_t c = buf[i]; unsigned char p[3] = { c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF }; fwrite(p, 1, 3, f); }
	fclose(f);
}
int main(int argc, char** argv) {
	if (argc < 3) { fprintf(stderr, "usage: %s ROM SCRIPT\n", argv[0]); return 2; }
	mLogSetDefaultLogger(&L);
	core = mCoreFind(argv[1]); if (!core || !core->init(core)) return 3;
	core->desiredVideoDimensions(core, &W, &H); buf = calloc(W * H, sizeof(color_t));
	core->setVideoBuffer(core, buf, W);
	mCoreInitConfig(core, NULL);
	if (!mCoreLoadFile(core, argv[1])) return 4;
	core->reset(core);
	FILE* s = fopen(argv[2], "r"); char line[512];
	while (fgets(line, sizeof line, s)) {
		char cmd[32], a[256] = "", b[64] = ""; if (sscanf(line, "%31s %255s %63s", cmd, a, b) < 1 || cmd[0] == '#') continue;
		if (!strcmp(cmd, "wait")) frames(atoi(a), 0);
		else if (!strcmp(cmd, "hold")) frames(atoi(b), parsekeys(a));
		else if (!strcmp(cmd, "shot")) { shot(a); printf("shot %s\n", a); }
		else if (!strcmp(cmd, "watch")) {
			struct ARMCore* cpu = core->cpu; uint32_t ring[64] = {0}, lr[64] = {0}; int ri = 0;
			uint32_t end = core->frameCounter(core) + atoi(a), last = 0; int hit = 0;
			while (core->frameCounter(core) < end) {
				uint32_t pc = cpu->gprs[ARM_PC];
				if (pc >= 0x02000000 && (pc < last || pc > last + 4)) { ring[ri & 63] = pc; lr[ri & 63] = cpu->gprs[ARM_LR]; ri++; }
				/* reset: execution restarts at the ROM entry point (0x08000000, +8 prefetch) or reset vector */
				if ((pc >= 0x08000000 && pc <= 0x08000008 && last > 0x08000100) || pc == 0x00000008 || pc == 0x00000004) {
					printf("RESET pc=0x%08x lr=0x%08x frame=%u\n", pc, cpu->gprs[ARM_LR], core->frameCounter(core));
					for (int k = ri - 64 < 0 ? 0 : ri - 64; k < ri; k++) printf("  pc 0x%08x lr 0x%08x\n", ring[k & 63], lr[k & 63]);
					hit = 1; break;
				}
				last = pc; core->step(core);
			}
			if (!hit) printf("watch: no exception vector in %s frames\n", a);
		}
		else if (!strcmp(cmd, "peek16")) { uint32_t ad = strtoul(a, NULL, 0); printf("peek16 %s = 0x%04x\n", a, core->busRead16(core, ad)); }
	}
	core->deinit(core); return 0;
}
