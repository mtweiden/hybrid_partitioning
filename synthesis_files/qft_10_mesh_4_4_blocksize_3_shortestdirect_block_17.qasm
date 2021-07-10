OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];
u3(1.5707963267948961, 3.086420008457935e-12, 2.1248270454511555) q[0];
u3(3.1415926535663035, 3.747714852665703, 5.743645707382346) q[1];
u3(4.712388980456718, 3.6819787771028403, 5.7561384178716555) q[2];
cx q[1], q[2];
u3(3.141592653612885, 2.8143632201600792, 3.5337737426712) q[1];
rx(1.5707963267948966) q[2];
rz(3.3281877175158265) q[2];
rx(1.5707963267948966) q[2];
rz(4.712388980384676) q[2];
cx q[1], q[2];
u3(4.712388980384643, 1.289046066126599, 2.795884482973821) q[1];
rx(1.5707963267948966) q[2];
rz(2.8417045643309984) q[2];
rx(1.5707963267948966) q[2];
rz(5.281045706699484) q[2];
cx q[1], q[0];
rx(1.5707963267948966) q[0];
rz(8.766272650429107e-17) q[0];
rx(1.5707963267948966) q[0];
rz(3.141592653589793) q[0];
u3(3.239767424014469, 6.097449476814632, 0.2817502622460414) q[1];
cx q[1], q[2];
u3(3.190680038802057, 1.4914451989787234, 3.327328494093245) q[1];
rx(1.5707963267948966) q[2];
rz(4.712388980397036) q[2];
rx(1.5707963267948966) q[2];
rz(0.35170745193984043) q[2];
cx q[1], q[0];
rx(1.5707963267948966) q[0];
rz(4.71238898038469) q[0];
rx(1.5707963267948966) q[0];
rz(1.1640277637766876) q[0];
u3(4.712388980375448, 2.8179634178476896, 0.07935113638393528) q[1];
cx q[1], q[2];
u3(3.141592653509915, 0.08692541592099651, 6.166693069534757) q[1];
rx(1.5707963267948966) q[2];
rz(6.28318530715631) q[2];
rx(1.5707963267948966) q[2];
rz(0.6399841652057864) q[2];
