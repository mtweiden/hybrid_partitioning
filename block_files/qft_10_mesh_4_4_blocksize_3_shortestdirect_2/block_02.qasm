OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
cx q[1], q[0];
u3(0.0, 0.0, -0.39269908169872414) q[0];
cx q[1], q[0];
u3(0.0, 0.0, 0.39269908169872414) q[0];
u3(0.0, 0.0, 0.19634954084936207) q[1];
cx q[1], q[2];
u3(0.0, 0.0, -0.19634954084936207) q[2];
cx q[1], q[2];
u3(0.0, 0.0, 0.09817477042468103) q[1];
u3(0.0, 0.0, 0.19634954084936207) q[2];
