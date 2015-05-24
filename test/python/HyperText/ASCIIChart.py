#!/usr/bin/python
from HyperText.HTML import BR, TABLE, TR, TH, TD, EM, quote_body
from HyperText.Documents import Document

t = TABLE()
tr = TR(TH(BR()))
for i in range(16): tr.append(TH(hex(i)))
t.append(tr)

for j in range(0,128,16):
    tr = TR(TH(hex(j)))
    t.append(tr)
    for i in range(16):
        v = i+j
        tr.append(TD(EM(v), BR(), quote_body(repr(chr(v)))))

d = Document(t)
print d
