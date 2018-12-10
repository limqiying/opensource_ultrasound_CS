//
//  main.cpp
//  cone
//
//  Created by CHEN Liqi on 10/19/18.
//  Copyright © 2018 CHEN Liqi. All rights reserved.
//

#include <GLUT/glut.h>
#include <OpenGL/OpenGL.h>
#include <math.h>
#include <GLUT/vvector.h>
#include <vector>
#include <iostream>

using namespace std;

// For dragging the view
static float c=M_PI/180.0f;
static int du=90,oldmy=-1,oldmx=-1;
//du - angle wrt y axis, y is up in OpenGL
static float r=1.5f,h=0.0f;

// For drawing a cone
vector<float> probe = {0.0, 0.0, 0.0};
vector<float> ending = {-0.5, 0.0, 0.0};
vector<float> randomPoint(3,0);
vector<float> orientation = {-1.0, 0.0, 0.0}; // unit vector
float spreadness = 25;
float resolution = 1;

void getRotated(vector<float>& rotated, vector<float> original, float angle, float axis_x, float axis_y, float axis_z){
    float rad = angle / 180 * 3.1416;
    float c = cosf(rad);
    float s = sinf(rad);
    float rotationMat[3][3] =
    { {powf(axis_x,2)*(1-c)+c, axis_x*axis_y*(1-c)+axis_z*s, axis_x*axis_z*(1-c)-axis_y*s},
      {axis_x*axis_y*(1-c)-axis_z*s, powf(axis_y,2)*(1-c)+c, axis_y*axis_z*(1-c)+axis_x*s},
      {axis_z*axis_x*(1-c)+axis_y*s, axis_y*axis_z*(1-c)-axis_x*s, powf(axis_z,2)*(1-c)+c}
    };
    MAT_DOT_VEC_3X3(rotated, rotationMat, original);
}

void display(){
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    glLoadIdentity();
    
    gluLookAt(r*cos(c*du), h, r*sin(c*du), 0, 0, 0, 0, 1, 0);

    // draw prob and axis
    glBegin(GL_LINES);
    glLineWidth(3.0);
    glColor3f(0.0, 0.0, 1.0);
    glVertex3f(probe[0], probe[1], probe[2]);
    glVertex3f(ending[0], ending[1], ending[2]);
    glEnd();
    
    // pick a random normal in 3D space
    vector<float> vec1(3, 0);
    VEC_DIFF(vec1, randomPoint, probe)
    vector<float> normal(3, 0);
    VEC_CROSS_PRODUCT(normal, orientation, vec1);
    VEC_NORMALIZE(normal);
    
    for(int i = 0; i < 360/resolution; i++){
        // draw one line on the cone
        vector<float> conePoint(3, 0);
        getRotated(conePoint, ending, spreadness, normal[0], normal[1], normal[2]);
        glBegin(GL_LINES);
        glLineWidth(3.0);
        glColor3f(0.0, 0.0, 1.0);
        glVertex3f(probe[0], probe[1], probe[2]);
        glVertex3f(conePoint[0], conePoint[1], conePoint[2]);
        glEnd();
        getRotated(normal, normal, resolution, orientation[0], orientation[1], orientation[2]);
    }
    
//    cout << conePoint[0] << " " << conePoint[1] << " " << conePoint[2] << endl;
    
    glFlush();
    
    glutSwapBuffers();
}


// Mouse click action: record old coordinate when click
void Mouse(int button, int state, int x, int y)
{
    if(state == GLUT_DOWN){
        oldmx = x;
        oldmy = y;
    }
}

// Mouse move action
void onMouseMove(int x,int y)
{
    du += x - oldmx;
    // move left-right
    h +=0.03f*(y-oldmy);
    // move up-down
    if(h>1.0f)
        h=1.0f;
    // limit watch point's y axis
    else
        if(h<-1.0f) h=-1.0f;
    oldmx=x;
    oldmy=y;
    
    // Render to display
    glutPostRedisplay();
}

void init()
{
    glEnable(GL_DEPTH_TEST);
}

void reshape(int w,int h)
{
    glViewport( 0, 0, w, h );
    
    glMatrixMode( GL_PROJECTION );
    
    glLoadIdentity();
    
    gluPerspective(75.0f, (float)w/h, 1.0f, 1000.0f);
    
    glMatrixMode( GL_MODELVIEW );
    
}

int main(int argc, char *argv[])
{
    randomPoint = {(float)(rand() % 100 - 50)/50, (float)(rand() % 100 - 50)/50, (float)(rand() % 100 - 50)/50};
    
    glutInit(&argc, argv);
    
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH );
    
    glutInitWindowPosition(100, 100);
    
    glutInitWindowSize(400, 400);
    
    glutCreateWindow("ScanCube");
    
    init();
    
    glutReshapeFunc( reshape );
    
    glutDisplayFunc(display);
    
    //    glutIdleFunc(selfMoving);
    
    glutMouseFunc(Mouse);
    
    glutMotionFunc(onMouseMove);
    
    glutMainLoop();
    
//    vector<float> rotated = {0, 0, 0};
//    vector<float> original = {1, 0, 0};
//    float angle = 90;
//    float x = 0;
//    float y = 0;
//    float z = 1;
//    
//    getRotated(rotated, original, angle, x, y, z);
//    
//    cout << rotated[0] << " " << rotated[1] << " " << rotated[2] << endl;

    
    return 0;

}
