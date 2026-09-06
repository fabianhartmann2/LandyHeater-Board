.PHONY: doctor check export-review clean

doctor:
	./scripts/kicad.sh doctor

check:
	./scripts/kicad.sh check

export-review:
	./scripts/kicad.sh export-review

clean:
	./scripts/kicad.sh clean
