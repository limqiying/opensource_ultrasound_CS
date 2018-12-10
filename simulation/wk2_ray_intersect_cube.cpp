#include <GLUT/glut.h>
#include <OpenGL/OpenGL.h>
#include <math.h>
#include <stdio.h>
#include <OpenGL/gl.h>
#include <OpenGl/glu.h>
#include <GLUT/vvector.h>
#include <vector>
#include <iostream>
#include <math.h>

using namespace std;

// ----------------------------------------------------------
// Global Variables
// ----------------------------------------------------------
// For rotate cube (degree)
double rotate_y = 0;
double rotate_x = 0;

// For moving probe
double step = -0.02;
double height = 0;
double inter_point = 0.01;

// For dragging the view
static float c=M_PI/180.0f;
static int du=90,oldmy=-1,oldmx=-1;
//du - angle wrt y axis, y is up in OpenGL
static float r=1.5f,h=0.0f;

// random rays
float lines[100][6];


bool rayPlaneIntersection(vector<float>& intersection, vector<float> ray, vector<float> probe,
                           vector<float> normal, vector<float> planePoint) {
    float temp;
    VEC_DOT_PRODUCT(temp,normal,ray);
    
    //check if the ray is parallel to the plane
    if (temp == 0) {
        return false;
    }
    
    float t = ((planePoint[0] - probe[0]) * normal[0] + (planePoint[1] - probe[1]) * normal[1] + (planePoint[2] - probe[2]) * normal[2]) / temp;
    intersection[0] = probe[0] + ray[0] * t;
    intersection[1] = probe[1] + ray[1] * t;
    intersection[2] = probe[2] + ray[2] * t;
    
    return true;
}


bool checkPointInTriangle(vector<float> point, vector<float> v1, vector<float> v2, vector<float> v3){
    vector<float> vec0 = {v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]};
    vector<float> vec1 = {v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]};
    vector<float> vec2 = {point[0] - v1[0], point[1] - v1[1], point[2] - v1[2]};
    
    float dot00, dot01, dot02, dot11, dot12;
    VEC_DOT_PRODUCT(dot00, vec0, vec0);
    VEC_DOT_PRODUCT(dot01, vec0, vec1);
    VEC_DOT_PRODUCT(dot02, vec0, vec2);
    VEC_DOT_PRODUCT(dot11, vec1, vec1);
    VEC_DOT_PRODUCT(dot12, vec1, vec2);
    
    float inverDeno = 1 / (dot00 * dot11 - dot01 * dot01) ;
    
    float u = (dot11 * dot02 - dot01 * dot12) * inverDeno ;
    if (u < 0 || u > 1) // if u out of range, return directly
    {
        return false ;
    }
    
    float v = (dot00 * dot12 - dot01 * dot02) * inverDeno ;
    if (v < 0 || v > 1) // if v out of range, return directly
    {
        return false ;
    }
    
    return u + v <= 1 ;
}


void display(void)
{
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    glLoadIdentity();
    
    gluLookAt(r*cos(c*du), h, r*sin(c*du), 0, 0, 0, 0, 1, 0);
    
    glPushMatrix();
    
    // Rotate when user changes rotate_x and rotate_y
    glRotatef( rotate_x, 1.0, 0.0, 0.0 );
    glRotatef( rotate_y, 0.0, 1.0, 0.0 );
    
    // FRONT
    glBegin(GL_POLYGON);
    glColor3f(   0.6,  0.6, 0.6 );
    glVertex3f(  0.3, -0.3, -0.3 );
    glVertex3f(  0.3,  0.3, -0.3 );
    glVertex3f( -0.3,  0.3, -0.3 );
    glVertex3f( -0.3, -0.3, -0.3 );
    glEnd();
    
    // BACK
    glBegin(GL_POLYGON);
    glColor3f(    0.5,  0.5, 0.5 );
    glVertex3f(  0.3, -0.3, 0.3 );
    glVertex3f(  0.3,  0.3, 0.3 );
    glVertex3f( -0.3,  0.3, 0.3 );
    glVertex3f( -0.3, -0.3, 0.3 );
    glEnd();
    
    // RIGHT
    glBegin(GL_POLYGON);
    glColor3f(   0.7,  0.7, 0.7 );
    glVertex3f( 0.3, -0.3, -0.3 );
    glVertex3f( 0.3,  0.3, -0.3 );
    glVertex3f( 0.3,  0.3,  0.3 );
    glVertex3f( 0.3, -0.3,  0.3 );
    glEnd();
    
    // LEFT
    glBegin(GL_POLYGON);
    glColor3f(    0.8,  0.8, 0.8 );
    glVertex3f( -0.3, -0.3,  0.3 );
    glVertex3f( -0.3,  0.3,  0.3 );
    glVertex3f( -0.3,  0.3, -0.3 );
    glVertex3f( -0.3, -0.3, -0.3 );
    glEnd();
    
    // TOP
    glBegin(GL_POLYGON);
    glColor3f(    0.4,  0.4, 0.4 );
    glVertex3f(  0.3,  0.3,  0.3 );
    glVertex3f(  0.3,  0.3, -0.3 );
    glVertex3f( -0.3,  0.3, -0.3 );
    glVertex3f( -0.3,  0.3,  0.3 );
    glEnd();
    
    // BOTTOM
    glBegin(GL_POLYGON);
    glColor3f(    0.3,  0.3, 0.3 );
    glVertex3f(  0.3, -0.3, -0.3 );
    glVertex3f(  0.3, -0.3,  0.3 );
    glVertex3f( -0.3, -0.3,  0.3 );
    glVertex3f( -0.3, -0.3, -0.3 );
    glEnd();
    
    glPopMatrix();
    
    glPushMatrix();
    
    // Define the cube
    vector<float> normals[3];
    normals[0] = {0, 0, 1};
    normals[1] = {1, 0, 0};
    normals[2] = {0, 1, 0};
    
    // FRONT: 0, BACK: 1, RIGHT: 2, LEFT: 3, TOP: 4, BOTTOM: 5
    vector<float> sides[6][4];
    
    sides[0][0] = {0.3, 0.3, 0.3};
    sides[0][1] = {0.3, -0.3, 0.3};
    sides[0][2] = {-0.3, -0.3, 0.3};
    sides[0][3] = {-0.3, 0.3, 0.3};
    
    sides[1][0] = {-0.3, 0.3, -0.3};
    sides[1][1] = {-0.3, -0.3, -0.3};
    sides[1][2] = {0.3, -0.3, -0.3};
    sides[1][3] = {0.3, 0.3, -0.3};
    
    sides[2][0] = {0.3, 0.3, -0.3};
    sides[2][1] = {0.3, -0.3, -0.3};
    sides[2][2] = {0.3, -0.3, 0.3};
    sides[2][3] = {0.3, 0.3, 0.3};
    
    sides[3][0] = {-0.3, 0.3, 0.3};
    sides[3][1] = {-0.3,-0.3, 0.3};
    sides[3][2] = {-0.3, -0.3, -0.3};
    sides[3][3] = {-0.3, 0.3, -0.3};
    
    sides[4][0] = {0.3, 0.3, -0.3};
    sides[4][1] = {0.3, 0.3, 0.3};
    sides[4][2] = {-0.3, 0.3, 0.3};
    sides[4][3] = {-0.3, 0.3, -0.3};
    
    sides[5][0] = {0.3, -0.3, 0.3};
    sides[5][1] = {0.3, -0.3, -0.3};
    sides[5][2] = {-0.3, -0.3, -0.3};
    sides[5][3] = {-0.3, -0.3, 0.3};
    
    
    // Define the probes
    glTranslatef(0, height, 0);
    
    for(int line = 0; line < 100; line++){
        
        // Probe - Straight Line
        vector<float> linePoint1 = {lines[line][0], lines[line][1], lines[line][2]};
        vector<float> linePoint2 = {lines[line][3], lines[line][4], lines[line][5]};
        glBegin(GL_LINES);
        glLineWidth(3.0);
        glColor3f(0.0, 0.0, 1.0);
        glVertex3f(linePoint1[0], linePoint1[1], linePoint1[2]);
        glVertex3f(linePoint2[0], linePoint2[1], linePoint2[2]);
        glEnd();
        
        // find intersections
        vector<float> intersection(3, 0);
        vector<float> ray = {linePoint1[0] - linePoint2[0], linePoint1[1] - linePoint2[1], linePoint1[2] - linePoint2[2]};
        vector<float> probe = {linePoint1[0], linePoint1[1], linePoint1[2]};
        
        // Draw intersection points
        glPointSize(7.0f);//set point size to 10 pixels
        glColor3f(1.0f,0.0f,0.0f); //red color
        int count = 0;
        for(int i = 0; i < 6 && count < 2; i++){
            if(!rayPlaneIntersection(intersection, ray, probe, normals[i/2], sides[i][0])){
                continue;
            }
            if(checkPointInTriangle(intersection, sides[i][0], sides[i][1], sides[i][2])){
                glBegin(GL_POINTS); //starts drawing of points
                glVertex3f(intersection[0],intersection[1],intersection[2]);
                glEnd();//end drawing of points
                //            cout << intersection[0] << " " << intersection[1] << " " << intersection[2] << endl;
                count++;
                continue;
            }
            if(checkPointInTriangle(intersection, sides[i][2], sides[i][3], sides[i][0])){
                glBegin(GL_POINTS); //starts drawing of points
                glVertex3f(intersection[0],intersection[1],intersection[2]);
                glEnd();//end drawing of points
                //            cout << intersection[0] << " " << intersection[1] << " " << intersection[2] << endl;
                count++;
                continue;
            }
        }
        
    }
    
    glPopMatrix();
    
    glFlush();
    
    glutSwapBuffers();
    
}

// Mouse click action: record old coordinate when click
void Mouse(int button, int state, int x, int y)
{
    if(state == GLUT_DOWN)
        oldmx = x;
    oldmy = y;
    
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

void selfMoving() {
    //    // Rotate cube
    //    rotate_y = (int)(rotate_y + 1) % 360;
    //    //rotate_x = (int)(rotate_x + 1) % 360;
    //
    //    //rotate_y = 0;
    //    rotate_x = 0;
    //
    
//        // Move probe
//        height = height + step;
//        if(height < -0.3)
//            step = -step;
//        if(height > 0.3)
//            step = -step;
    
    // Render to display
    glutPostRedisplay();
}

int main(int argc, char *argv[])
{
    for(int i = 0; i < 100; i++){
        for(int j = 0; j < 6; j++){
            lines[i][j] = (float)(rand() % 100 - 50)/50;
        }
    }
    
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

    return 0;
    
}
