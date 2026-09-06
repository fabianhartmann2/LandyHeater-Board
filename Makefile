.PHONY: doctor sch-check check export-phase2 phase2-audit export-review clean

doctor:
	./scripts/kicad.sh doctor

check:
	./scripts/kicad.sh check

sch-check:
	./scripts/kicad.sh sch-check

export-phase2:
	./scripts/kicad.sh export-phase2

phase2-audit:
	python3 scripts/audit_phase2.py

export-review:
	./scripts/kicad.sh export-review

clean:
	./scripts/kicad.sh clean
