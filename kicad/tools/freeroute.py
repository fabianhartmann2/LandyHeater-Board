"""Routing der langsamen Signale mit Freerouting (Schritt 6.5, Methode „Hybrid").

Ablauf (alles reproduzierbar, Projektdatei bleibt unberührt):
 0. Projektboard: frühere Freerouting-Gruppe entfernen.
 1. Arbeitskopie in <repo>/build/freeroute: alle vorhandenen Leiterbahnen/Vias (Handrouting, Flächenvias) sperren
    → im DSN „protect", Freerouting verändert sie nicht. Außenlagen-GND-Füllungen (L1/L4) entfernen, sonst
    exportiert KiCad sie als Ebene und Freerouting meidet die ganze Lage. Die R:-Flächen bleiben (Netz-Flächen).
    Netzklassen nur in der Kopie: Abstand 0,2 mm (globale Regel aus LandyHeater.kicad_dru, die das DSN nicht kennt),
    USB 0,15 mm; Breite Power 0,4 mm (offen sind nur der Taster-LED-Strompfad und die 1-mA-Diagnosezuleitungen).
 2. DSN-Export, Freerouting 2.1.0 (Java 21, Optimierer aus – sonst schreibt 2.1.0 einen veralteten Stand ins SES).
 3. SES-Import in die Kopie; neue Leiterbahnen/Vias (nicht schon im Projekt) werden als Gruppe GROUP ins Projekt
    übernommen. Danach Innenlagen füllen.

Aufruf (KiCad-Python, Board im Projektordner): python3 tools/freeroute.py LandyHeater.kicad_pcb [Laufzeit je Lauf hh:mm:ss] [Läufe]
"""
import json
import re
import os
import shutil
import subprocess
import sys
import pcbnew

GROUP = 'Freerouting (tools/freeroute.py)'
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, '..', '..', 'build', 'freeroute')
JAVA = '/opt/homebrew/opt/openjdk@21/bin/java'
JAR = os.path.expanduser('~/.kicad-mcp/freerouting.jar')
# Netze, deren Handroute nur ein Fan-out ist (Stich + Via): nicht gesperrt – Freerouting 2.1.0 kommt mit
# gesperrten Signal-Vias schlecht zurecht (Probe: 85 statt 9 offene Verbindungen) und darf sie nutzen oder ersetzen
FREE_NETS = {'/ESP32 und RTC/RTC_INT_N', 'AUTOTERM_TX_3V3', 'AUTOTERM_RX_3V3', 'AUTOTERM_OE', '1WIRE_DQ'}
# vollständig von Hand geroutete Netze: Freerouting-Zusätze darauf (z. B. Splitter an gesperrten Bahnen) werden verworfen
DONE_NETS = {'USB_DN_C', 'USB_DP_C', 'Net-(U4-USB_D-)', 'Net-(U4-USB_D+)', '/Versorgung/CC1', '/Versorgung/CC2',
             '/Versorgung/USB_VBUS', '/Versorgung/BATT_12V_IN', '/Versorgung/SW_BUCK', 'Net-(U3-BOOT)', 'Net-(U3-VCC)',
             'Net-(U2-ILM)', 'Net-(U2-DVDT)', 'Net-(U2-ITIMER)', 'Net-(U2-EN{slash}UVLO)', 'Net-(U2-OVLO)'}
PLANE_NETS = {'GND', '3V3_CORE', 'VIN_SYS'}   # über Flächenvias angebunden (tools/route_planevias.py)
CLASS = {'Default': (0.2, 0.2), 'Extern': (0.2, 0.3), 'Power': (0.2, 0.4), 'USB': (0.15, 0.25)}   # Abstand, Breite


def run(stage, *args):
    subprocess.run([sys.executable, os.path.abspath(__file__), '--stage', stage] + list(args), check=True)


def key(t, mm=pcbnew.ToMM):
    if t.GetClass() == 'PCB_VIA':
        return ('V', t.GetNetname(), round(mm(t.GetPosition().x), 3), round(mm(t.GetPosition().y), 3))
    a = (round(mm(t.GetStart().x), 3), round(mm(t.GetStart().y), 3)); c = (round(mm(t.GetEnd().x), 3), round(mm(t.GetEnd().y), 3))
    return ('T', t.GetNetname(), t.GetLayer(), min(a, c), max(a, c))


def stage_clean(path):
    b = pcbnew.LoadBoard(path)
    old = [g for g in b.Groups() if g.GetName() == GROUP]
    for it in [it for g in old for it in g.GetItems()] + old:
        b.Remove(it)
    b.Save(path); os._exit(0)


def stage_prepare(work_pcb):
    b = pcbnew.LoadBoard(work_pcb)
    outer = [z for z in b.Zones() if z.GetZoneName() in ('GND L1', 'GND L4')]
    # Netzflächen des Handroutings („R: …", F.Cu) zusätzlich als Sperrflächen (die Flächen bleiben für den eigenen
    # Netz-Zusammenhang): Freerouting behandelt DSN-Flächen auf
    # Signallagen als durchlässig für fremde Netze (Probe: 12V_PROT/DIAG_K quer durch die Regler-Flächen)
    rz = [(z.GetZoneName(), [(o.CPoint(i).x, o.CPoint(i).y) for o in [z.Outline().Outline(0)] for i in range(o.PointCount())])
          for z in b.Zones() if z.GetZoneName().startswith('R: ') and z.GetLayer() == pcbnew.F_Cu]
    for name, pts in rz:
        k = pcbnew.ZONE(b); k.SetIsRuleArea(True); k.SetZoneName('Sperre ' + name); k.SetLayer(pcbnew.F_Cu)
        k.SetDoNotAllowTracks(True); k.SetDoNotAllowVias(True); k.SetDoNotAllowPads(False); k.SetDoNotAllowZoneFills(False)
        ps = pcbnew.SHAPE_POLY_SET(); ps.NewOutline()
        for x, y in pts: ps.Append(x, y)
        k.SetOutline(ps); ps.thisown = 0; b.Add(k)
    for t in b.GetTracks():
        t.SetLocked(t.GetNetname() not in FREE_NETS)
    b.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)   # L3 ist geteilte Versorgungsebene: kein Routing darauf
    for z in outer:
        b.Remove(z)
    b.Save(work_pcb); os._exit(0)


def stage_export(work_pcb, dsn):
    b = pcbnew.LoadBoard(work_pcb)
    ok = pcbnew.ExportSpecctraDSN(b, dsn)
    print('DSN-Export:', 'ok' if ok else 'FEHLER', flush=True); os._exit(0 if ok else 1)


def stage_import(work_pcb, ses):
    b = pcbnew.LoadBoard(work_pcb)
    ok = pcbnew.ImportSpecctraSES(b, ses)
    b.Save(work_pcb)
    print('SES-Import:', 'ok' if ok else 'FEHLER', flush=True); os._exit(0 if ok else 1)


def stage_transfer(path, work_pcb):
    b = pcbnew.LoadBoard(path); w = pcbnew.LoadBoard(work_pcb)
    have = {key(t) for t in b.GetTracks()}
    got = {key(t) for t in w.GetTracks()}
    lost = {k for k in have - got if k[1] not in FREE_NETS}   # gesperrte Bahnen, die Freerouting verändert hätte
    dropped = {k for k in have - got if k[1] in FREE_NETS}   # Fan-out-Elemente, die Freerouting ersetzt hat
    grp = pcbnew.PCB_GROUP(b); grp.SetName(GROUP); b.Add(grp)
    nt = nv = 0
    for t in w.GetTracks():
        if key(t) in have or t.GetNetname() in DONE_NETS or t.GetNetname() in PLANE_NETS: continue
        if t.GetClass() == 'PCB_TRACK' and t.GetLength() < pcbnew.FromMM(0.05): continue   # Splitter aus dem SES-Import
        net = b.FindNet(t.GetNetname())
        if t.GetClass() == 'PCB_VIA':
            v = pcbnew.PCB_VIA(b); v.SetPosition(t.GetPosition()); v.SetWidth(t.GetWidth(pcbnew.F_Cu)); v.SetDrill(t.GetDrill())
            v.SetNet(net); b.Add(v); grp.AddItem(v); nv += 1
        else:
            n = pcbnew.PCB_TRACK(b); n.SetStart(t.GetStart()); n.SetEnd(t.GetEnd()); n.SetWidth(t.GetWidth()); n.SetLayer(t.GetLayer())
            n.SetNet(net); b.Add(n); grp.AddItem(n); nt += 1
    b.Save(path)
    print(f'übernommen: {nt} Leiterbahnen, {nv} Vias; gesperrte Elemente verändert: {len(lost)}; Fan-out ersetzt: {len(dropped)}', flush=True)
    for k in sorted(lost, key=str)[:10]: print('   verändert:', k)
    os._exit(0)


def main(path, timeout, tries):
    path = os.path.abspath(path); proj = os.path.splitext(path)[0]
    os.makedirs(WORK, exist_ok=True)
    run('clean', path)
    wp = os.path.join(WORK, 'fr.kicad_pcb')
    shutil.copy(path, wp); shutil.copy(proj + '.kicad_dru', os.path.join(WORK, 'fr.kicad_dru'))
    pro = json.load(open(proj + '.kicad_pro'))
    for c in pro['net_settings']['classes']:
        c['clearance'], c['track_width'] = CLASS[c['name']]
    json.dump(pro, open(os.path.join(WORK, 'fr.kicad_pro'), 'w'), indent=2)
    run('prepare', wp)
    dsn, ses = os.path.join(WORK, 'fr.dsn'), os.path.join(WORK, 'fr.ses')
    if os.path.exists(ses): os.remove(ses)
    run('export', wp, dsn)
    # Freerouting arbeitet zufallsgesteuert und bleibt teils in lokalen Minima hängen (Probe: 84 statt 10 offene
    # Verbindungen bei gleicher Ausgangslage) – mehrere Läufe nacheinander, der mit den wenigsten offenen wird übernommen.
    # Nutzungsstatistik von Freerouting abgeschaltet.
    # Viakosten 8 statt 50: mit 50 meidet Freerouting den Lagenwechsel nach L4 fast ganz (Probe 3 min: 93 → 16–22 offen)
    procs = []
    for k in range(tries):
        out, lg = os.path.join(WORK, f'fr_{k}.ses'), os.path.join(WORK, f'freerouting_{k}.log')
        if os.path.exists(out): os.remove(out)
        procs.append((out, lg, subprocess.Popen(
            [JAVA, '-jar', JAR, '-de', dsn, '-do', out, '--router.optimizer.enabled=false', f'--router.job_timeout={timeout}',
             '--router.scoring.via_costs=8', '--gui.enabled=false', '--usage_and_diagnostic_data.disable_analytics=true'],
            stdout=open(lg, 'w'), stderr=subprocess.STDOUT, cwd=WORK)))
        # nacheinander (parallele Läufe teilen sich die CPU und werden deutlich schlechter); harte Zeitgrenze, weil ein
        # einzelner Durchgang die job_timeout-Grenze ignorieren kann (beobachtet: 34 min)
        h, m_, s_ = map(int, timeout.split(':'))
        try:
            procs[-1][2].wait(timeout=h * 3600 + m_ * 60 + s_ + 60)
        except subprocess.TimeoutExpired:
            procs[-1][2].kill(); procs[-1][2].wait()
    best = None
    for k, (out, lg, pr) in enumerate(procs):
        pr.wait()
        m = re.findall(r'"incomplete_count": (\d+)', open(lg).read())
        n_open = int(m[-1]) if m and os.path.exists(out) else 10 ** 6
        print(f'Lauf {k + 1}/{tries}: {n_open} offen', flush=True)
        if best is None or n_open < best[0]: best = (n_open, out)
    shutil.copy(best[1], ses)
    run('import', wp, ses)
    run('transfer', path, wp)
    subprocess.run([sys.executable, os.path.join(HERE, 'zones.py'), path, '--fill-stage'], check=True)


if __name__ == '__main__':
    if '--stage' in sys.argv:
        i = sys.argv.index('--stage'); st = sys.argv[i + 1]; a = sys.argv[i + 2:]
        {'clean': stage_clean, 'prepare': stage_prepare, 'export': stage_export, 'import': stage_import,
         'transfer': stage_transfer}[st](*a)
    else:
        main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '00:03:00', int(sys.argv[3]) if len(sys.argv) > 3 else 4)
