OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
cx q[1], q[3];
u3(0.0, 0.0, -0.01227184630308513) q[3];
cx q[1], q[3];
u3(0.0, 0.0, 0.006135923151542565) q[1];
u3(0.0, 0.0, 0.01227184630308513) q[3];
cx q[1], q[4];
cx q[2], q[3];
u3(0.0, 0.0, -0.02454369260617026) q[3];
u3(0.0, 0.0, -0.006135923151542565) q[4];
cx q[1], q[4];
cx q[2], q[3];
u3(0.0, 0.0, 0.0030679615757712823) q[1];
u3(0.0, 0.0, 0.01227184630308513) q[2];
u3(0.0, 0.0, 0.02454369260617026) q[3];
u3(0.0, 0.0, 0.006135923151542565) q[4];
cx q[0], q[3];
cx q[2], q[4];
u3(0.0, 0.0, -0.04908738521234052) q[3];
u3(0.0, 0.0, -0.01227184630308513) q[4];
cx q[0], q[3];
cx q[2], q[4];
u3(0.0, 0.0, 0.02454369260617026) q[0];
u3(0.0, 0.0, 0.006135923151542565) q[2];
u3(0.0, 0.0, 0.04908738521234052) q[3];
u3(0.0, 0.0, 0.01227184630308513) q[4];
cx q[0], q[4];
u3(0.0, 0.0, -0.02454369260617026) q[4];
cx q[0], q[4];
u3(0.0, 0.0, 0.01227184630308513) q[0];
u3(0.0, 0.0, 0.02454369260617026) q[4];