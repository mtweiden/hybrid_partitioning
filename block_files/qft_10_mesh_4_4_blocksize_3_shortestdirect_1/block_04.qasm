OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
cx q[0], q[2];
u3(0.0, 0.0, -0.04908738521234052) q[2];
cx q[0], q[2];
u3(0.0, 0.0, 0.02454369260617026) q[0];
u3(0.0, 0.0, 0.04908738521234052) q[2];
cx q[1], q[2];
u3(0.0, 0.0, -0.09817477042468103) q[2];
cx q[1], q[2];
u3(0.0, 0.0, 0.04908738521234052) q[1];
u3(0.0, 0.0, 0.09817477042468103) q[2];
