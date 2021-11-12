OPENQASM 2.0;
include "qelib1.inc";
qreg q[17];
u3(0,0,1.5585245) q[0];
u3(0,0,1.5585245) q[1];
u3(0,0,1.5462526) q[2];
u3(0,0,1.5217089) q[3];
u3(0,0,1.4726216) q[4];
u3(0,0,7*pi/16) q[5];
u3(0,0,3*pi/8) q[6];
u3(0,0,pi/4) q[7];
u3(pi,0,4.7062531) q[8];
u3(0,0,6.2709135) q[9];
u3(0,0,3.117049) q[10];
u3(0,0,3.0925053) q[11];
u3(0,0,3.0434179) q[12];
u3(0,0,15*pi/16) q[13];
u3(0,0,7*pi/8) q[14];
u3(0,0,3*pi/4) q[15];
u3(pi/2,0,pi) q[16];
cx q[15],q[16];
u3(0,0,7*pi/4) q[16];
cx q[15],q[16];
u3(pi/2,0,pi/2) q[15];
u3(0,0,pi/4) q[16];
cx q[14],q[16];
u3(0,0,15*pi/8) q[16];
cx q[14],q[16];
cx q[14],q[15];
u3(0,0,7*pi/4) q[15];
cx q[14],q[15];
u3(pi/2,0,pi/2) q[14];
u3(0,0,pi/4) q[15];
u3(0,0,pi/8) q[16];
cx q[13],q[16];
u3(0,0,6.0868358) q[16];
cx q[13],q[16];
cx q[13],q[15];
u3(0,0,15*pi/8) q[15];
cx q[13],q[15];
cx q[13],q[14];
u3(0,0,7*pi/4) q[14];
cx q[13],q[14];
u3(pi/2,0,pi/2) q[13];
u3(0,0,pi/4) q[14];
u3(0,0,pi/8) q[15];
u3(0,0,pi/16) q[16];
cx q[12],q[16];
u3(0,0,6.1850105) q[16];
cx q[12],q[16];
cx q[12],q[15];
u3(0,0,6.0868358) q[15];
cx q[12],q[15];
cx q[12],q[14];
u3(0,0,15*pi/8) q[14];
cx q[12],q[14];
cx q[12],q[13];
u3(0,0,7*pi/4) q[13];
cx q[12],q[13];
u3(pi/2,0,pi/2) q[12];
u3(0,0,pi/4) q[13];
u3(0,0,pi/8) q[14];
u3(0,0,pi/16) q[15];
u3(0,0,pi/32) q[16];
cx q[11],q[16];
u3(0,0,6.2340979) q[16];
cx q[11],q[16];
cx q[11],q[15];
u3(0,0,6.1850105) q[15];
cx q[11],q[15];
cx q[11],q[14];
u3(0,0,6.0868358) q[14];
cx q[11],q[14];
cx q[11],q[13];
u3(0,0,15*pi/8) q[13];
cx q[11],q[13];
cx q[11],q[12];
u3(0,0,7*pi/4) q[12];
cx q[11],q[12];
u3(pi/2,0,pi/2) q[11];
u3(0,0,pi/4) q[12];
u3(0,0,pi/8) q[13];
u3(0,0,pi/16) q[14];
u3(0,0,pi/32) q[15];
u3(0,0,pi/64) q[16];
cx q[10],q[16];
u3(0,0,6.2586416) q[16];
cx q[10],q[16];
cx q[10],q[15];
u3(0,0,6.2340979) q[15];
cx q[10],q[15];
cx q[10],q[14];
u3(0,0,6.1850105) q[14];
cx q[10],q[14];
cx q[10],q[13];
u3(0,0,6.0868358) q[13];
cx q[10],q[13];
cx q[10],q[12];
u3(0,0,15*pi/8) q[12];
cx q[10],q[12];
cx q[10],q[11];
u3(0,0,7*pi/4) q[11];
cx q[10],q[11];
u3(pi/2,0,pi/2) q[10];
u3(0,0,pi/4) q[11];
u3(0,0,pi/8) q[12];
u3(0,0,pi/16) q[13];
u3(0,0,pi/32) q[14];
u3(0,0,pi/64) q[15];
u3(0,0,pi/128) q[16];
cx q[9],q[16];
u3(0,0,6.2709135) q[16];
cx q[9],q[16];
u3(pi,0,3.1538645) q[16];
cx q[8],q[16];
u3(pi,0,3.1354567) q[16];
cx q[8],q[16];
u3(0,0,pi/512) q[16];
cx q[7],q[16];
u3(0,0,7*pi/4) q[16];
cx q[7],q[16];
u3(0,0,pi/4) q[16];
cx q[6],q[16];
u3(0,0,15*pi/8) q[16];
cx q[6],q[16];
u3(0,0,pi/8) q[16];
cx q[5],q[16];
u3(0,0,6.0868358) q[16];
cx q[5],q[16];
u3(0,0,pi/16) q[16];
cx q[4],q[16];
u3(0,0,6.1850105) q[16];
cx q[4],q[16];
u3(0,0,pi/32) q[16];
cx q[3],q[16];
u3(0,0,6.2340979) q[16];
cx q[3],q[16];
u3(0,0,pi/64) q[16];
cx q[2],q[16];
u3(0,0,6.2586416) q[16];
cx q[2],q[16];
u3(0,0,pi/128) q[16];
cx q[1],q[16];
u3(0,0,6.2709135) q[16];
cx q[1],q[16];
u3(0,0,pi/256) q[16];
cx q[0],q[16];
u3(0,0,6.2770494) q[16];
cx q[0],q[16];
u3(0,0,pi/512) q[16];
cx q[9],q[15];
u3(0,0,6.2586416) q[15];
cx q[9],q[15];
u3(pi,0,3.1661363) q[15];
cx q[8],q[15];
u3(pi,0,3.1293208) q[15];
cx q[8],q[15];
u3(pi/2,0,4.7246608) q[15];
cx q[7],q[15];
u3(pi/2,3*pi/2,3*pi) q[15];
cx q[6],q[15];
u3(0,0,7*pi/4) q[15];
cx q[6],q[15];
u3(0,0,pi/4) q[15];
cx q[5],q[15];
u3(0,0,15*pi/8) q[15];
cx q[5],q[15];
u3(0,0,pi/8) q[15];
cx q[4],q[15];
u3(0,0,6.0868358) q[15];
cx q[4],q[15];
u3(0,0,pi/16) q[15];
cx q[3],q[15];
u3(0,0,6.1850105) q[15];
cx q[3],q[15];
u3(0,0,pi/32) q[15];
cx q[2],q[15];
u3(0,0,6.2340979) q[15];
cx q[2],q[15];
u3(0,0,pi/64) q[15];
cx q[1],q[15];
u3(0,0,6.2586416) q[15];
cx q[1],q[15];
u3(0,0,pi/128) q[15];
cx q[0],q[15];
u3(0,0,6.2709135) q[15];
cx q[0],q[15];
u3(0,0,pi/256) q[15];
cx q[9],q[14];
u3(0,0,6.2340979) q[14];
cx q[9],q[14];
u3(pi,0,3.19068) q[14];
cx q[8],q[14];
u3(pi,0,3.117049) q[14];
cx q[8],q[14];
u3(pi/2,0,4.7369327) q[14];
cx q[6],q[14];
u3(pi/2,3*pi/2,3*pi) q[14];
cx q[5],q[14];
u3(0,0,7*pi/4) q[14];
cx q[5],q[14];
u3(0,0,pi/4) q[14];
cx q[4],q[14];
u3(0,0,15*pi/8) q[14];
cx q[4],q[14];
u3(0,0,pi/8) q[14];
cx q[3],q[14];
u3(0,0,6.0868358) q[14];
cx q[3],q[14];
u3(0,0,pi/16) q[14];
cx q[2],q[14];
u3(0,0,6.1850105) q[14];
cx q[2],q[14];
u3(0,0,pi/32) q[14];
cx q[1],q[14];
u3(0,0,6.2340979) q[14];
cx q[1],q[14];
u3(0,0,pi/64) q[14];
cx q[0],q[14];
u3(0,0,6.2586416) q[14];
cx q[0],q[14];
u3(0,0,pi/128) q[14];
cx q[9],q[13];
u3(0,0,6.1850105) q[13];
cx q[9],q[13];
u3(pi,0,3.2397674) q[13];
cx q[8],q[13];
u3(pi,0,3.0925053) q[13];
cx q[8],q[13];
u3(pi/2,0,4.7614764) q[13];
cx q[5],q[13];
u3(pi/2,3*pi/2,3*pi) q[13];
cx q[4],q[13];
u3(0,0,7*pi/4) q[13];
cx q[4],q[13];
u3(0,0,pi/4) q[13];
cx q[3],q[13];
u3(0,0,15*pi/8) q[13];
cx q[3],q[13];
u3(0,0,pi/8) q[13];
cx q[2],q[13];
u3(0,0,6.0868358) q[13];
cx q[2],q[13];
u3(0,0,pi/16) q[13];
cx q[1],q[13];
u3(0,0,6.1850105) q[13];
cx q[1],q[13];
u3(0,0,pi/32) q[13];
cx q[0],q[13];
u3(0,0,6.2340979) q[13];
cx q[0],q[13];
u3(0,0,pi/64) q[13];
cx q[9],q[12];
u3(0,0,6.0868358) q[12];
cx q[9],q[12];
u3(pi,0,3.3379422) q[12];
cx q[8],q[12];
u3(pi,0,3.0434179) q[12];
cx q[8],q[12];
u3(pi/2,0,4.8105637) q[12];
cx q[4],q[12];
u3(pi/2,3*pi/2,3*pi) q[12];
cx q[3],q[12];
u3(0,0,7*pi/4) q[12];
cx q[3],q[12];
u3(0,0,pi/4) q[12];
cx q[2],q[12];
u3(0,0,15*pi/8) q[12];
cx q[2],q[12];
u3(0,0,pi/8) q[12];
cx q[1],q[12];
u3(0,0,6.0868358) q[12];
cx q[1],q[12];
u3(0,0,pi/16) q[12];
cx q[0],q[12];
u3(0,0,6.1850105) q[12];
cx q[0],q[12];
u3(0,0,pi/32) q[12];
cx q[9],q[11];
u3(0,0,15*pi/8) q[11];
cx q[9],q[11];
u3(pi,0,9*pi/8) q[11];
cx q[8],q[11];
u3(pi,0,15*pi/16) q[11];
cx q[8],q[11];
u3(pi/2,0,4.9087385) q[11];
cx q[3],q[11];
u3(pi/2,3*pi/2,3*pi) q[11];
cx q[2],q[11];
u3(0,0,7*pi/4) q[11];
cx q[2],q[11];
u3(0,0,pi/4) q[11];
cx q[1],q[11];
u3(0,0,15*pi/8) q[11];
cx q[1],q[11];
u3(0,0,pi/8) q[11];
cx q[0],q[11];
u3(0,0,6.0868358) q[11];
cx q[0],q[11];
u3(0,0,pi/16) q[11];
cx q[9],q[10];
u3(0,0,7*pi/4) q[10];
cx q[9],q[10];
u3(pi,0,5*pi/4) q[10];
cx q[8],q[10];
u3(pi,0,7*pi/8) q[10];
cx q[8],q[10];
u3(pi/2,0,13*pi/8) q[10];
cx q[2],q[10];
u3(pi/2,3*pi/2,3*pi) q[10];
cx q[1],q[10];
u3(0,0,7*pi/4) q[10];
cx q[1],q[10];
u3(0,0,pi/4) q[10];
cx q[0],q[10];
u3(0,0,15*pi/8) q[10];
cx q[0],q[10];
u3(0,0,pi/8) q[10];
u3(pi/2,0,pi/2) q[9];
cx q[8],q[9];
u3(pi,0,3*pi/4) q[9];
cx q[8],q[9];
u3(pi/2,0,7*pi/4) q[9];
cx q[1],q[9];
u3(pi/2,3*pi/2,3*pi) q[9];
cx q[0],q[9];
u3(0,0,7*pi/4) q[9];
cx q[0],q[9];
cx q[0],q[8];
u3(pi,0,4.7062531) q[8];
u3(0,0,pi/4) q[9];
cx q[8],q[9];
u3(0,0,pi/4) q[9];
cx q[8],q[9];
cx q[8],q[10];
u3(0,0,pi/8) q[10];
cx q[8],q[10];
u3(0,0,15*pi/8) q[10];
cx q[8],q[11];
u3(0,0,pi/16) q[11];
cx q[8],q[11];
u3(0,0,6.0868358) q[11];
cx q[8],q[12];
u3(0,0,pi/32) q[12];
cx q[8],q[12];
u3(0,0,6.1850105) q[12];
cx q[8],q[13];
u3(0,0,pi/64) q[13];
cx q[8],q[13];
u3(0,0,6.2340979) q[13];
cx q[8],q[14];
u3(0,0,pi/128) q[14];
cx q[8],q[14];
u3(0,0,6.2586416) q[14];
cx q[8],q[15];
u3(0,0,pi/256) q[15];
cx q[8],q[15];
u3(0,0,6.2709135) q[15];
cx q[8],q[16];
u3(0,0,pi/512) q[16];
cx q[8],q[16];
u3(0,0,6.2770494) q[16];
u3(pi/2,4.7246608,3*pi/4) q[9];
cx q[9],q[10];
u3(0,0,pi/4) q[10];
cx q[9],q[10];
u3(pi/2,4.7369327,3*pi/4) q[10];
cx q[9],q[11];
u3(0,0,pi/8) q[11];
cx q[9],q[11];
u3(0,0,15*pi/8) q[11];
cx q[10],q[11];
u3(0,0,pi/4) q[11];
cx q[10],q[11];
u3(pi/2,4.7614764,3*pi/4) q[11];
cx q[9],q[12];
u3(0,0,pi/16) q[12];
cx q[9],q[12];
u3(0,0,6.0868358) q[12];
cx q[10],q[12];
u3(0,0,pi/8) q[12];
cx q[10],q[12];
u3(0,0,15*pi/8) q[12];
cx q[11],q[12];
u3(0,0,pi/4) q[12];
cx q[11],q[12];
u3(pi/2,4.8105638,3*pi/4) q[12];
cx q[9],q[13];
u3(0,0,pi/32) q[13];
cx q[9],q[13];
u3(0,0,6.1850105) q[13];
cx q[10],q[13];
u3(0,0,pi/16) q[13];
cx q[10],q[13];
u3(0,0,6.0868358) q[13];
cx q[11],q[13];
u3(0,0,pi/8) q[13];
cx q[11],q[13];
u3(0,0,15*pi/8) q[13];
cx q[12],q[13];
u3(0,0,pi/4) q[13];
cx q[12],q[13];
u3(pi/2,4.9087385,3*pi/4) q[13];
cx q[9],q[14];
u3(0,0,pi/64) q[14];
cx q[9],q[14];
u3(0,0,6.2340979) q[14];
cx q[10],q[14];
u3(0,0,pi/32) q[14];
cx q[10],q[14];
u3(0,0,6.1850105) q[14];
cx q[11],q[14];
u3(0,0,pi/16) q[14];
cx q[11],q[14];
u3(0,0,6.0868358) q[14];
cx q[12],q[14];
u3(0,0,pi/8) q[14];
cx q[12],q[14];
u3(0,0,15*pi/8) q[14];
cx q[13],q[14];
u3(0,0,pi/4) q[14];
cx q[13],q[14];
u3(pi/2,13*pi/8,3*pi/4) q[14];
cx q[9],q[15];
u3(0,0,pi/128) q[15];
cx q[9],q[15];
u3(0,0,6.2586416) q[15];
cx q[10],q[15];
u3(0,0,pi/64) q[15];
cx q[10],q[15];
u3(0,0,6.2340979) q[15];
cx q[11],q[15];
u3(0,0,pi/32) q[15];
cx q[11],q[15];
u3(0,0,6.1850105) q[15];
cx q[12],q[15];
u3(0,0,pi/16) q[15];
cx q[12],q[15];
u3(0,0,6.0868358) q[15];
cx q[13],q[15];
u3(0,0,pi/8) q[15];
cx q[13],q[15];
u3(0,0,15*pi/8) q[15];
cx q[14],q[15];
u3(0,0,pi/4) q[15];
cx q[14],q[15];
u3(pi/2,7*pi/4,3*pi/4) q[15];
cx q[9],q[16];
u3(0,0,pi/256) q[16];
cx q[9],q[16];
u3(0,0,6.2709135) q[16];
cx q[10],q[16];
u3(0,0,pi/128) q[16];
cx q[10],q[16];
u3(0,0,6.2586416) q[16];
cx q[11],q[16];
u3(0,0,pi/64) q[16];
cx q[11],q[16];
u3(0,0,6.2340979) q[16];
cx q[12],q[16];
u3(0,0,pi/32) q[16];
cx q[12],q[16];
u3(0,0,6.1850105) q[16];
cx q[13],q[16];
u3(0,0,pi/16) q[16];
cx q[13],q[16];
u3(0,0,6.0868358) q[16];
cx q[14],q[16];
u3(0,0,pi/8) q[16];
cx q[14],q[16];
u3(0,0,15*pi/8) q[16];
cx q[15],q[16];
u3(0,0,pi/4) q[16];
cx q[15],q[16];
u3(pi/2,0,3*pi/4) q[16];
