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

check() {
	doctor
	mkdir -p "$report_dir"

	"$kicad_cli" sch erc \
		--severity-all \
		--exit-code-violations \
		--output "$report_dir/erc.rpt" \
		"$schematic"

	"$kicad_cli" pcb drc \
		--severity-all \
		--exit-code-violations \
		--schematic-parity \
		--output "$report_dir/drc.rpt" \
		"$board"

	printf 'ERC- und DRC-Berichte: %s\n' "$report_dir"
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
	check)
		check
		;;
	export-review)
		export_review
		;;
	clean)
		clean
		;;
	*)
		printf 'Verwendung: %s {doctor|check|export-review|clean}\n' "$0" >&2
		exit 2
		;;
esac
