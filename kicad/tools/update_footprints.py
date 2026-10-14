"""Footprints aus der Bibliothek neu laden (entspricht „Footprints aus Bibliothek aktualisieren“ in KiCad).

Behält Position, Drehung, Lage, Referenz, Wert, alle Felder, Attribute, Schaltplan-Verknüpfung und Pad-Netze.
Anlass: Rundungsabweichungen von 1 nm in Grafikkoordinaten nach wiederholtem Drehen (DRC lib_footprint_mismatch).
Aufruf (KiCad-Python, Board im Projektordner): python3 tools/update_footprints.py LandyHeater.kicad_pcb [REF ...]
Ohne REF werden alle Footprints aktualisiert.
"""
import os, sys
import pcbnew

STD = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints'
HERE = os.path.dirname(os.path.abspath(sys.argv[1]))
LOCAL = {'LandyHeater': os.path.join(HERE, 'libraries', 'LandyHeater.pretty')}


def libpath(nick):
    return LOCAL.get(nick, os.path.join(STD, nick + '.pretty'))


def main(path, refs):
    b = pcbnew.LoadBoard(path)
    done = []
    for old in list(b.GetFootprints()):
        r = old.GetReference()
        if refs and r not in refs:
            continue
        fid = old.GetFPID()
        new = pcbnew.FootprintLoad(libpath(fid.GetLibNickname().wx_str()), fid.GetLibItemName().wx_str())
        if new is None:
            print('nicht gefunden:', r, fid.Format().wx_str()); continue
        new.SetFPID(fid)
        new.SetParent(b)
        # Felder (Referenz, Wert, Footprint, Datenblatt, Beschreibung, eigene Felder) mit Sichtbarkeit und Lage
        for fld in old.GetFields():
            name = fld.GetName()
            if new.HasField(name):
                nf = new.GetField(name)
            else:
                new.SetField(name, fld.GetText()); nf = new.GetField(name)
            nf.SetText(fld.GetText()); nf.SetVisible(fld.IsVisible()); nf.SetLayer(fld.GetLayer())
            nf.SetPosition(fld.GetPosition()); nf.SetTextAngle(fld.GetTextAngle())
        new.SetPath(old.GetPath()); new.SetSheetname(old.GetSheetname()); new.SetSheetfile(old.GetSheetfile())
        attr_lib = new.GetAttributes()   # Montageart (SMD/THT) aus der Bibliothek, Flags vom alten Footprint
        new.SetBoardOnly(old.IsBoardOnly()); new.SetExcludedFromBOM(old.IsExcludedFromBOM())
        new.SetExcludedFromPosFiles(old.IsExcludedFromPosFiles()); new.SetDNP(old.IsDNP())
        new.SetLocked(old.IsLocked())
        def key(p):   # Padnummer + Lage im Footprint (mehrere Pads mit gleicher Nummer, z. B. Schirm, EPAD)
            q = p.GetFPRelativePosition(); return (p.GetNumber(), round(q.x / 1000), round(q.y / 1000))
        nets = {key(p): p.GetNet() for p in old.Pads()}
        b.Remove(old)
        b.Add(new)
        # Lage/Drehung erst nach dem Einfügen setzen, Felder bleiben relativ korrekt
        new.SetPosition(old.GetPosition()); new.SetOrientation(old.GetOrientation())
        if old.GetLayer() != new.GetLayer():
            new.Flip(new.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
        for fld in old.GetFields():
            nf = new.GetField(fld.GetName())
            if nf is not None: nf.SetPosition(fld.GetPosition()); nf.SetTextAngle(fld.GetTextAngle())
        for p in new.Pads():
            if key(p) in nets: p.SetNet(nets[key(p)])
            else: print('Pad ohne Gegenstück:', r, p.GetNumber())
        done.append(r)
    b.Save(path)
    print(f'{len(done)} Footprints aktualisiert')


if __name__ == '__main__':
    main(sys.argv[1], set(sys.argv[2:]))
