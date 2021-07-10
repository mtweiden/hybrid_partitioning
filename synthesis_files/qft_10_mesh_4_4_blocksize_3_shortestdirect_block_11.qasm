OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];
u3(3.1415927526078598, 0.2212309541833104, 4.561225685470049) q[0];
u3(3.14159265099799, 4.694650124290223, 5.878761450021004) q[1];
u3(4.933298214382376e-10, 3.23176559691211, 4.112885388416405) q[2];
cx q[0], q[2];
u3(2.522158905337729e-13, 0.5291934045767931, 4.441661375441477) q[0];
rx(1.5707963267948966) q[2];
rz(6.283185307179586) q[2];
rx(1.5707963267948966) q[2];
rz(6.234097921970415) q[2];
cx q[1], q[2];
u3(3.1415926535898566, 3.6490096140384356, 5.778235548763109) q[1];
rx(1.5707963267948966) q[2];
rz(8.881784197001252e-16) q[2];
rx(1.5707963267948966) q[2];
rz(8.881784197001252e-16) q[2];
cx q[0], q[2];
u3(3.141592554571727, 1.7384590897519425, 1.0830553484147434) q[0];
rx(1.5707963267948966) q[2];
rz(6.283185307179585) q[2];
rx(1.5707963267948966) q[2];
rz(3.0434178831653798) q[2];
cx q[1], q[2];
u3(2.5918033222208633e-09, 0.44748527728231824, 3.688309370513701) q[1];
rx(1.5707963267948966) q[2];
rz(3.1415926530964637) q[2];
rx(1.5707963267948966) q[2];
rz(5.368981784667654) q[2];
