#!/bin/sh

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(CDPATH= cd -- "$script_dir/.." && pwd)
project_name="LandyHeater-Board"
project_dir="$repo_dir/hardware"
schematic="$project_dir/$project_name.kicad_sch"
board="$project_dir/$project_name.kicad_pcb"
build_dir="$repo_dir/build"
report_dir="$build_dir/reports"
review_dir="$build_dir/review"
output_pdf_dir="$repo_dir/output/pdf"
output_bom_dir="$repo_dir/output/bom"
output_report_dir="$repo_dir/output/reports"

find_kicad_cli() {
	if [ -n "${KICAD_CLI_OVERRIDE:-}" ] && [ -x "$KICAD_CLI_OVERRIDE" ]; then
		printf '%s\n' "$KICAD_CLI_OVERRIDE"
		return
	fi

	if command -v kicad-cli >/dev/null 2>&1; then
		command -v kicad-cli
		return
	fi

	macos_cli="/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
	if [ -x "$macos_cli" ]; then
		printf '%s\n' "$macos_cli"
		return
	fi

	printf '%s\n' "KiCad CLI wurde nicht gefunden. Setze KICAD_CLI_OVERRIDE auf den vollständigen Pfad." >&2
	exit 1
}

kicad_cli=$(find_kicad_cli)

doctor() {
	printf 'KiCad CLI: %s\n' "$kicad_cli"
	printf 'KiCad Version: '
	"$kicad_cli" --version

	for required_file in \
		"$project_dir/$project_name.kicad_pro" \
		"$schematic" \
		"$board" \
		"$project_dir/sym-lib-table" \
		"$project_dir/fp-lib-table" \
		"$project_dir/libraries/symbols/LandyHeater.kicad_sym"
	do
		if [ ! -f "$required_file" ]; then
			printf 'Fehlende Projektdatei: %s\n' "$required_file" >&2
			exit 1
		fi
	done

	if [ ! -d "$project_dir/libraries/footprints/LandyHeater.pretty" ]; then
		printf 'Fehlende Footprint-Bibliothek: %s\n' "$project_dir/libraries/footprints/LandyHeater.pretty" >&2
		exit 1
	fi

	printf 'Projektgerüst: vollständig\n'
}

sch_check() {
	doctor
	mkdir -p "$report_dir"

	"$kicad_cli" sch erc \
		--severity-all \
		--exit-code-violations \
		--output "$report_dir/erc.rpt" \
		"$schematic"

	printf 'ERC-Bericht: %s\n' "$report_dir/erc.rpt"
}

check() {
	sch_check

	"$kicad_cli" pcb drc \
		--severity-all \
		--exit-code-violations \
		--output "$report_dir/drc.rpt" \
		"$board"

	printf 'DRC-Bericht: %s\n' "$report_dir/drc.rpt"
}

export_phase2() {
	sch_check
	mkdir -p "$output_pdf_dir" "$output_bom_dir" "$output_report_dir" "$report_dir"

	"$kicad_cli" sch erc \
		--severity-all \
		--exit-code-violations \
		--output "$output_report_dir/$project_name-ERC-Phase2.rpt" \
		"$schematic"

	"$kicad_cli" sch export pdf \
		--output "$output_pdf_dir/$project_name-schematic-Phase2.pdf" \
		"$schematic"

	"$kicad_cli" sch export bom \
		--fields 'Reference,Value,Footprint,Datasheet,Manufacturer,MPN,Assembly,Notes' \
		--group-by 'Value,Footprint,Manufacturer,MPN,Assembly' \
		--output "$output_bom_dir/$project_name-BOM-Phase2.csv" \
		"$schematic"

	"$kicad_cli" sch export netlist \
		--output "$report_dir/phase2.net" \
		"$schematic"

	python3 "$script_dir/audit_phase2.py"

	printf 'Phase-2-PDF: %s\n' "$output_pdf_dir/$project_name-schematic-Phase2.pdf"
	printf 'Phase-2-BOM: %s\n' "$output_bom_dir/$project_name-BOM-Phase2.csv"
	printf 'Phase-2-Audit: %s\n' "$report_dir/phase2-audit.txt"
	printf 'Phase-2-ERC-Kopie: %s\n' "$output_report_dir/$project_name-ERC-Phase2.rpt"
}

export_review() {
	check
	mkdir -p "$review_dir"
	step_output="$review_dir/$project_name-board-only.step"

	"$kicad_cli" sch export pdf \
		--black-and-white \
		--output "$review_dir/$project_name-schematic.pdf" \
		"$schematic"

	"$kicad_cli" pcb export pdf \
		--black-and-white \
		--include-border-title \
		--layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.SilkS,B.SilkS,Edge.Cuts \
		--mode-multipage \
		--output "$review_dir/$project_name-pcb-layers.pdf" \
		"$board"

	if [ -f "$step_output" ]; then
		find "$step_output" -delete
	fi

	if ! "$kicad_cli" pcb export step \
		--board-only \
		--output "$step_output" \
		"$board" 2>"$report_dir/step-export.stderr"
	then
		printf 'STEP-Export fehlgeschlagen:\n' >&2
		cat "$report_dir/step-export.stderr" >&2
		exit 1
	fi

	if [ ! -s "$step_output" ]; then
		printf 'STEP-Export wurde nicht erzeugt: %s\n' "$step_output" >&2
		exit 1
	fi

	printf 'Review-Dateien: %s\n' "$review_dir"
}

clean() {
	if [ -d "$build_dir" ]; then
		find "$build_dir" -mindepth 1 -delete
		rmdir "$build_dir"
	fi
	printf 'Generierte Dateien entfernt.\n'
}

case "${1:-check}" in
	doctor)
		doctor
		;;
	sch-check)
		sch_check
		;;
	check)
		check
		;;
	export-phase2)
		export_phase2
		;;
	export-review)
		export_review
		;;
	clean)
		clean
		;;
	*)
		printf 'Verwendung: %s {doctor|sch-check|check|export-phase2|export-review|clean}\n' "$0" >&2
		exit 2
		;;
esac
