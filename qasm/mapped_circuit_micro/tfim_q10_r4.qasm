OPENQASM 2.0;
include "qelib1.inc";
qreg node[10];
creg c[10];
u3(pi/2,0,pi) node[0];
u3(pi/2,0,pi) node[1];
u3(pi/2,0,pi) node[2];
u3(pi/2,0,pi) node[3];
u3(pi/2,0,pi) node[4];
u3(pi/2,0,pi) node[5];
u3(pi/2,0,pi) node[6];
u3(pi/2,0,pi) node[7];
u3(pi/2,0,pi) node[8];
u3(pi/2,0,pi) node[9];
u1(6.1753763) node[0];
u1(6.1753763) node[1];
u1(6.1753763) node[2];
u1(6.1753763) node[3];
u1(6.1753763) node[4];
u1(6.1753763) node[5];
u1(6.1753763) node[6];
u1(6.1753763) node[7];
u1(6.1753763) node[8];
u1(6.1753763) node[9];
u3(pi/2,0,pi) node[0];
u3(pi/2,0,pi) node[1];
u3(pi/2,0,pi) node[2];
u3(pi/2,0,pi) node[3];
u3(pi/2,0,pi) node[4];
u3(pi/2,0,pi) node[5];
u3(pi/2,0,pi) node[6];
u3(pi/2,0,pi) node[7];
u3(pi/2,0,pi) node[8];
u3(pi/2,0,pi) node[9];
cx node[2],node[7];
u1(6.1752659) node[7];
cx node[2],node[7];
u3(pi/2,0,pi) node[2];
cx node[7],node[6];
u1(6.1762582) node[2];
u1(6.1752659) node[6];
u3(pi/2,0,pi) node[2];
cx node[7],node[6];
cx node[6],node[1];
u3(pi/2,0,pi) node[7];
u1(6.1752659) node[1];
u1(6.1762582) node[7];
cx node[6],node[1];
u3(pi/2,0,pi) node[7];
cx node[1],node[0];
cx node[2],node[7];
u3(pi/2,0,pi) node[6];
u1(6.1752659) node[0];
u1(6.1762582) node[6];
u1(6.1752659) node[7];
cx node[1],node[0];
cx node[2],node[7];
u3(pi/2,0,pi) node[6];
cx node[0],node[5];
u3(pi/2,0,pi) node[1];
u3(pi/2,0,pi) node[2];
cx node[7],node[6];
u1(6.1762582) node[1];
u1(6.1780149) node[2];
u1(6.1752659) node[5];
u1(6.1752659) node[6];
cx node[0],node[5];
u3(pi/2,0,pi) node[1];
u3(pi/2,0,pi) node[2];
cx node[7],node[6];
u3(pi/2,0,pi) node[0];
cx node[6],node[1];
u3(pi/2,0,pi) node[7];
u1(6.1762582) node[0];
u1(6.1752659) node[1];
u1(6.1780149) node[7];
u3(pi/2,0,pi) node[0];
cx node[6],node[1];
u3(pi/2,0,pi) node[7];
cx node[1],node[0];
cx node[2],node[7];
u3(pi/2,0,pi) node[6];
u1(6.1752659) node[0];
u1(6.1780149) node[6];
u1(6.1752659) node[7];
cx node[1],node[0];
cx node[2],node[7];
u3(pi/2,0,pi) node[6];
u3(pi/2,0,pi) node[1];
u3(pi/2,0,pi) node[2];
cx node[7],node[6];
u1(6.1780149) node[1];
u1(6.1806319) node[2];
u1(6.1752659) node[6];
u3(pi/2,0,pi) node[1];
u3(pi/2,0,pi) node[2];
cx node[7],node[6];
cx node[6],node[1];
u3(pi/2,0,pi) node[7];
u1(6.1752659) node[1];
u1(6.1806319) node[7];
cx node[6],node[1];
u3(pi/2,0,pi) node[7];
cx node[2],node[7];
u3(pi/2,0,pi) node[6];
u1(6.1806319) node[6];
u1(6.1752659) node[7];
cx node[2],node[7];
u3(pi/2,0,pi) node[6];
cx node[7],node[6];
u1(6.1752659) node[6];
cx node[7],node[6];
cx node[7],node[8];
cx node[8],node[7];
cx node[7],node[8];
cx node[6],node[7];
cx node[8],node[9];
cx node[7],node[6];
cx node[9],node[8];
cx node[6],node[7];
cx node[8],node[9];
cx node[4],node[9];
cx node[5],node[6];
cx node[9],node[4];
u1(6.1752659) node[6];
cx node[4],node[9];
cx node[5],node[6];
u3(pi/2,0,pi) node[5];
u1(6.1762582) node[5];
u3(pi/2,0,pi) node[5];
cx node[0],node[5];
u1(6.1752659) node[5];
cx node[0],node[5];
u3(pi/2,0,pi) node[0];
u1(6.1780149) node[0];
u3(pi/2,0,pi) node[0];
cx node[1],node[0];
u1(6.1752659) node[0];
cx node[1],node[0];
u3(pi/2,0,pi) node[1];
u1(6.1806319) node[1];
u3(pi/2,0,pi) node[1];
cx node[1],node[2];
cx node[2],node[7];
cx node[1],node[2];
u1(6.1752659) node[1];
cx node[2],node[7];
cx node[1],node[2];
cx node[2],node[7];
cx node[1],node[2];
cx node[2],node[7];
cx node[2],node[3];
cx node[3],node[2];
cx node[2],node[3];
cx node[2],node[7];
cx node[7],node[2];
cx node[2],node[7];
cx node[6],node[7];
u1(6.1752659) node[7];
cx node[6],node[7];
u3(pi/2,0,pi) node[6];
cx node[7],node[8];
u1(6.1762582) node[6];
u1(6.1752659) node[8];
u3(pi/2,0,pi) node[6];
cx node[7],node[8];
cx node[5],node[6];
u3(pi/2,0,pi) node[7];
cx node[8],node[9];
u1(6.1752659) node[6];
u1(6.1762582) node[7];
u1(6.1752659) node[9];
cx node[5],node[6];
u3(pi/2,0,pi) node[7];
cx node[8],node[9];
u3(pi/2,0,pi) node[5];
cx node[6],node[7];
u3(pi/2,0,pi) node[8];
u3(pi/2,0,pi) node[9];
u1(6.1780149) node[5];
u1(6.1752659) node[7];
u1(6.1762582) node[8];
u1(6.1762582) node[9];
u3(pi/2,0,pi) node[5];
cx node[6],node[7];
u3(pi/2,0,pi) node[8];
u3(pi/2,0,pi) node[9];
cx node[0],node[5];
u3(pi/2,0,pi) node[6];
cx node[7],node[8];
u1(6.1752659) node[5];
u1(6.1780149) node[6];
u1(6.1752659) node[8];
cx node[0],node[5];
u3(pi/2,0,pi) node[6];
cx node[7],node[8];
u3(pi/2,0,pi) node[0];
cx node[5],node[6];
u3(pi/2,0,pi) node[7];
cx node[8],node[9];
u1(6.1806319) node[0];
u1(6.1752659) node[6];
u1(6.1780149) node[7];
u1(6.1752659) node[9];
u3(pi/2,0,pi) node[0];
cx node[5],node[6];
u3(pi/2,0,pi) node[7];
cx node[8],node[9];
cx node[1],node[0];
u3(pi/2,0,pi) node[5];
cx node[6],node[7];
u3(pi/2,0,pi) node[8];
u3(pi/2,0,pi) node[9];
u1(6.1752659) node[0];
u1(6.1806319) node[5];
u1(6.1752659) node[7];
u1(6.1780149) node[8];
u1(6.1780149) node[9];
cx node[1],node[0];
u3(pi/2,0,pi) node[5];
cx node[6],node[7];
u3(pi/2,0,pi) node[8];
u3(pi/2,0,pi) node[9];
cx node[0],node[5];
u3(pi/2,0,pi) node[6];
cx node[7],node[8];
u1(6.1752659) node[5];
u1(6.1806319) node[6];
u1(6.1752659) node[8];
cx node[0],node[5];
u3(pi/2,0,pi) node[6];
cx node[7],node[8];
cx node[5],node[6];
u3(pi/2,0,pi) node[7];
cx node[8],node[9];
u1(6.1752659) node[6];
u1(6.1806319) node[7];
u1(6.1752659) node[9];
cx node[5],node[6];
u3(pi/2,0,pi) node[7];
cx node[8],node[9];
cx node[6],node[7];
u3(pi/2,0,pi) node[8];
u3(pi/2,0,pi) node[9];
u1(6.1752659) node[7];
u1(6.1806319) node[8];
u1(6.1806319) node[9];
cx node[6],node[7];
u3(pi/2,0,pi) node[8];
u3(pi/2,0,pi) node[9];
cx node[7],node[8];
u1(6.1752659) node[8];
cx node[7],node[8];
cx node[8],node[9];
u1(6.1752659) node[9];
cx node[8],node[9];
