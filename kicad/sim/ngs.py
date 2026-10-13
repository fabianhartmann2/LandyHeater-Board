"""Minimaler libngspice-Treiber (ctypes): laedt eine Netzliste, fuehrt sie aus, liefert Vektoren."""
import ctypes as C, sys
LIB = '/Applications/KiCad/KiCad.app/Contents/Frameworks/libngspice.0.dylib'
ng = C.CDLL(LIB)
OUT = C.CFUNCTYPE(C.c_int, C.c_char_p, C.c_int, C.c_void_p)
EXIT = C.CFUNCTYPE(C.c_int, C.c_int, C.c_bool, C.c_bool, C.c_int, C.c_void_p)
log = []
_o = OUT(lambda s, i, p: (log.append(s.decode(errors='replace')), 0)[1])
_x = EXIT(lambda *a: 0)
ng.ngSpice_Init(_o, _o, _x, None, None, None, None)
class VI(C.Structure):
    _fields_ = [('name', C.c_char_p), ('type', C.c_int), ('flags', C.c_short), ('realdata', C.POINTER(C.c_double)), ('compdata', C.c_void_p), ('length', C.c_int)]
ng.ngGet_Vec_Info.restype = C.POINTER(VI)
def run(netlist):
    lines = [l for l in netlist.strip().splitlines()] + ['.end']
    arr = (C.c_char_p * (len(lines) + 1))(*[l.encode() for l in lines], None)
    ng.ngSpice_Command(b'destroy all'); ng.ngSpice_Circ(arr); ng.ngSpice_Command(b'run')
def vec(name):
    p = ng.ngGet_Vec_Info(name.encode())
    if not p: raise KeyError(name)
    v = p.contents; return [v.realdata[i] for i in range(v.length)]
