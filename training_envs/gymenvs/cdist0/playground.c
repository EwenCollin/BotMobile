#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "playground.h"

/*
#define GRID_SIZE_X 600
#define GRID_SIZE_Y 600
#define BASE_GRID_X 9
#define BASE_GRID_Y 9
#define DISTANCE_RESOLUTION 16
//#define PI 3.1415926
#define MAX_DIST 1000000

#define MAX_SPEED 10
//#define steering_force 0.03
#define STATE_HISTORY 5
#define STATE_SIZE 6

#define CAR_SIZE_X 23
#define CAR_SIZE_Y 10
#define LID_RAY_NB 4


#define HISTORY_MOD 16
*/

//float steering_force = 0.03;
//float pi = 3.1415926;

//const float pi = 3.1415926;


int terrain_grid[9][9] = {
    {1,1,1,1,1,1,1,1,1},
    {1,0,0,0,1,0,0,0,1},
    {1,0,1,0,1,0,1,0,1},
    {1,0,1,0,0,0,1,0,1},
    {1,0,1,1,1,1,1,0,1},
    {1,0,1,1,1,0,0,0,1},
    {1,0,1,1,1,0,1,0,1},
    {1,0,0,0,0,0,0,0,1},
    {1,1,1,1,1,1,1,1,1}
};

/*
float lid_angles[4] = {
    -(float)3.1415926/4, 0, (float)3.1415926/4, (float)3.1415926
};*/

float lid_angles[MAX_LID_RAYS];

float lid_distances[MAX_LID_RAYS];

int lid_ray_nb = 0;

float state_buffer[(MAX_LID_RAYS + 2)*STATE_HISTORY];

int start_pos_x = (int) 218;
int start_pos_y = (int) 72;

int episode_done = 0;

int dist_save_a = MAX_DIST;
int dist_save_b = 1;


float start_rotation = (float) 3.1415926/2;

int terrain[GRID_SIZE_X][GRID_SIZE_Y];
int terrain_dist[DISTANCE_RESOLUTION*BASE_GRID_X][DISTANCE_RESOLUTION*BASE_GRID_Y];

int collisions[GRID_SIZE_X][GRID_SIZE_Y];

int distances[DISTANCE_RESOLUTION*BASE_GRID_X*DISTANCE_RESOLUTION*BASE_GRID_Y];

void generate_dist_grid(int [DISTANCE_RESOLUTION*BASE_GRID_X][DISTANCE_RESOLUTION*BASE_GRID_Y], int [BASE_GRID_X][BASE_GRID_Y]);
void generate_terrain(int [GRID_SIZE_X][GRID_SIZE_Y], int [BASE_GRID_X][BASE_GRID_Y]);
void generate_distances(int [DISTANCE_RESOLUTION*BASE_GRID_X*DISTANCE_RESOLUTION*BASE_GRID_Y], int [DISTANCE_RESOLUTION*BASE_GRID_X][DISTANCE_RESOLUTION*BASE_GRID_Y], int, int);

void load_terrain_file(char *);


void set_lid_ray_nb(int);
void set_lid_rays(float []);

void add_collision_point(int, int);
void reset_collision_points();
int is_collision(int, int);


int coords_to_one(int, int, int);
int one_to_coords_x(int, int);
int one_to_coords_y(int, int);
int is_wall(int, int);
int is_wall_grid(int, int);

int get_done_status();
float * get_state();
int * get_distances();

float get_position_x();
float get_position_y();
float get_rotation();
float get_speed();
float get_direction();
int get_step_count();
int get_dist_save_a();
int get_dist_save_b();
int get_distance_at(float, float);

float cast_ray(float, float, float);
float cast_ray_x(float, float, float);
float cast_ray_y(float, float, float);

float rotate_point_around_x(float, float, float, float, float);
float rotate_point_around_y(float, float, float, float, float);
int check_collide_terrain(float, float, float);

int check_collide_dynamic(float, float, float);
void add_car_collision_points(float, float, float);

void reset();
void lid_scan();
void set_state(float, float, float);
float step(float, float, float);
void set_step_data(float, float, float, float, float, int, int, int, int);

int get_reward(float, float);
void init();


float current_pos_x = 0.0;
float current_pos_y = 0.0;
float current_direction = 0.0;
float current_speed = 0.0;
float current_rotation = 0.0;
int current_step_count = 0;

void init() {
    //generate_terrain(terrain, terrain_grid);
    generate_dist_grid(terrain_dist, terrain_grid);
    generate_distances(distances, terrain_dist, start_pos_x, start_pos_y);
}

void set_lid_ray_nb(int nb) {
    lid_ray_nb = nb;

}
void set_lid_rays(float *ray_angles) {
    for (int i = 0; i < lid_ray_nb; i++) {
        lid_angles[i] = ray_angles[i];
    }
}

void load_terrain_file(char *filename) {
    FILE *fp = fopen(filename, "r");
    for(int i = 0; i < GRID_SIZE_X; i++) {
        for (int j = 0; j < GRID_SIZE_Y; j++) {
            fscanf(fp, "%d,", &terrain[i][j]);
        }
    }
    fclose(fp);
    //generate_distances(distances, terrain, )
}


void reset_collision_points() {
    for(int i = 0; i < GRID_SIZE_X; i++) {
        for (int j = 0; j < GRID_SIZE_Y; j++) {
            collisions[i][j] = 0;
        }
    }
}

void add_collision_point(int x, int y) {
    collisions[x][y] = 1;
}

int is_collision(int x, int y) {
    return collisions[x][y];
}


int get_dist_save_a() {
    return dist_save_a;
}
int get_dist_save_b() {
    return dist_save_b;
}

float get_speed() {
    return current_speed;
}
float get_direction() {
    return current_direction;
}
int get_step_count() {
    return current_step_count;
}

float get_position_x() {
    return current_pos_x;
}

float get_position_y() {
    return current_pos_y;
}

float get_rotation() {
    return current_rotation;
}

int is_wall(int x, int y) {
    return terrain[x][y];
}

int is_wall_grid(int x, int y) {
    return terrain_grid[x][y];
}

int * get_distances(){
    return distances;
}

/*
int main() {
    printf("HELLO");
    return 0;
}*/

float * get_state() {
    return state_buffer;
}

int get_done_status() {
    return episode_done;
}


void set_step_data(float px, float py, float rt, float sp, float dr, int sc, int ds, int dist_sa, int dist_sb) {
    current_pos_x = px;
    current_pos_y = py;
    current_rotation = rt;
    current_speed = sp;
    current_direction = dr;
    current_step_count = sc;
    episode_done = ds;
    dist_save_a = dist_sa;
    dist_save_b = dist_sb;
}


float step(float acceleration, float turning, float dt) {
    float a_t = acceleration * dt;
    current_speed += a_t;
    if (current_speed > (float) MAX_SPEED) {
        current_speed = (float) MAX_SPEED;
    } else if (current_speed < (float) - MAX_SPEED) {
        current_speed = -(float)MAX_SPEED;
    }
    float tn_t = turning * dt;
    current_direction += tn_t;
    
    if (current_direction > (float) MAX_TURN) {
        current_direction = (float) MAX_TURN;
    } else if (current_direction < (float) - MAX_TURN) {
        current_direction = (float) - MAX_TURN;
    }
    current_step_count++;


    //float r_t = fmodf(current_rotation + asinf(current_speed*dt*sinf(current_direction*0.1)/((float)WHEEL_SPACING)), 2.0*(float)3.1415926);
    
    float r_t = fmodf(current_rotation + current_speed*tanf(current_direction/20.0)*dt*0.05, 2.0*(float)3.1415926);
    float x_t = current_pos_x + dt*current_speed*cosf(r_t);
    float y_t = current_pos_y + dt*current_speed*sinf(r_t);


    current_pos_x = x_t;
    current_pos_y = y_t;
    current_rotation = r_t;

    set_state(current_pos_x, current_pos_y, current_rotation);
    int collide_dynamic = check_collide_dynamic((float)CAR_SIZE_X/(float)2.0, (float)CAR_SIZE_Y/(float)2.0 , r_t);
    if (check_collide_terrain((float)CAR_SIZE_X/(float)2.0, (float)CAR_SIZE_Y/(float)2.0 , r_t) || collide_dynamic) {
        episode_done = 1;
        return -(int)COLLIDE_REWARD;
    }
    return (float)get_reward(current_pos_x, current_pos_y);
    float side_distanceA = cast_ray(current_pos_x, current_pos_y, current_rotation + 3.1415926*0.5);
    float side_distanceB = cast_ray(current_pos_x, current_pos_y, current_rotation - 3.1415926*0.5);

    float track_centering = (side_distanceA > side_distanceB) ? side_distanceB/side_distanceA : side_distanceA/side_distanceB;

    //float speed_score = (current_speed > 3) ? (current_speed)/((float)MAX_SPEED) : (current_speed - 3)/(3 + (float)MAX_SPEED);//(float)(current_speed + (float)MAX_SPEED)/(2.0*(float)MAX_SPEED);//get_reward(current_pos_x, current_pos_y);
    //return speed_score;///2 + track_centering/2;
    //set_state()
    //fmodf
}

int get_distance_at(float x, float y) {
    int dist_grid_x = (int)(((float)DISTANCE_RESOLUTION*BASE_GRID_X)*x/((float)GRID_SIZE_X));
    int dist_grid_y = (int)(((float)DISTANCE_RESOLUTION*BASE_GRID_Y)*y/((float)GRID_SIZE_Y));
    return distances[coords_to_one(dist_grid_x, dist_grid_y, DISTANCE_RESOLUTION*BASE_GRID_X)];
}

int get_reward(float px, float py) {
    int dist_grid_x = (int)(((float)DISTANCE_RESOLUTION*BASE_GRID_X)*px/((float)GRID_SIZE_X));
    int dist_grid_y = (int)(((float)DISTANCE_RESOLUTION*BASE_GRID_Y)*py/((float)GRID_SIZE_Y));
    int current_distance = distances[coords_to_one(dist_grid_x, dist_grid_y, DISTANCE_RESOLUTION*BASE_GRID_X)];
    int distance_score = -1;
    if (current_distance - dist_save_a > 0) {
        distance_score = 1;
    } else if (current_distance - dist_save_a == 0) {
        distance_score = dist_save_b;
    }
    dist_save_a = current_distance;
    dist_save_b = distance_score;

    return distance_score;
}

void set_state(float px, float py, float rot) {
    if (current_step_count % HISTORY_MOD == 0) {
        for (int i = 0; i < (lid_ray_nb+2)*(STATE_HISTORY - 1); i++) {
            state_buffer[i] = state_buffer[i+STATE_SIZE];
        }
    }
    lid_scan();
    for (int i = (lid_ray_nb+2)*(STATE_HISTORY - 1); i < (lid_ray_nb+2)*STATE_HISTORY; i++) {
        int j = i - (lid_ray_nb+2)*(STATE_HISTORY - 1);
        if (j < lid_ray_nb) {
            state_buffer[i] = lid_distances[j];
        }
    }
    state_buffer[(lid_ray_nb+2)*STATE_HISTORY - 2] = current_speed;
    state_buffer[(lid_ray_nb+2)*STATE_HISTORY - 1] = current_direction;
}

void lid_scan() {
    for(int i = 0; i < lid_ray_nb; i++) {
        lid_distances[i] = cast_ray(current_pos_x, current_pos_y, current_rotation + lid_angles[i]);
    }
}

void reset() {
    for (int i = 0; i < STATE_HISTORY*STATE_SIZE; i++) {
        state_buffer[i] = 0;
    }
    episode_done = 0;

    dist_save_a = MAX_DIST;
    dist_save_b = 1;

    current_direction = 0.0;
    current_pos_x = (float)start_pos_x;
    current_pos_y = (float)start_pos_y;
    current_rotation = start_rotation;
    current_step_count = 0;
    current_speed = (float)MAX_SPEED;
    set_state(current_pos_x, current_pos_y, current_rotation);
}


int check_collide_terrain(float x, float y, float rot) {
    for (int i = 0; i < CAR_SIZE_X; i++) {
        int j = CAR_SIZE_Y*(i%2);
        float px = rotate_point_around_x((float) i, (float)j, rot, x, y);
        float py = rotate_point_around_y((float) i, (float)j, rot, x, y);
        if (terrain[(int)(px + current_pos_x)][(int)(py + current_pos_y)]) return 1;
    }
    for (int j = 0; j < CAR_SIZE_Y; j++) {
        int i = CAR_SIZE_X*(j%2);
        float px = rotate_point_around_x((float) i, (float)j, rot, x, y);
        float py = rotate_point_around_y((float) i, (float)j, rot, x, y);
        if (terrain[(int)(px + current_pos_x)][(int)(py + current_pos_y)]) return 1;
    }

    return 0;
}

void add_car_collision_points(float x, float y, float rot) {
    for (int i = 0; i < CAR_SIZE_X; i++) {
        int j = CAR_SIZE_Y*(i%2);
        float px = rotate_point_around_x((float) i, (float)j, rot, x, y);
        float py = rotate_point_around_y((float) i, (float)j, rot, x, y);
        collisions[(int)(px + current_pos_x)][(int)(py + current_pos_y)] = 1;
    }
    for (int j = 0; j < CAR_SIZE_Y; j++) {
        int i = CAR_SIZE_X*(j%2);
        float px = rotate_point_around_x((float) i, (float)j, rot, x, y);
        float py = rotate_point_around_y((float) i, (float)j, rot, x, y);
        collisions[(int)(px + current_pos_x)][(int)(py + current_pos_y)] = 1;
    }

}

int check_collide_dynamic(float x, float y, float rot) {
    for (int i = 0; i < CAR_SIZE_X; i++) {
        int j = CAR_SIZE_Y*(i%2);
        float px = rotate_point_around_x((float) i, (float)j, rot, x, y);
        float py = rotate_point_around_y((float) i, (float)j, rot, x, y);
        if (collisions[(int)(px + current_pos_x)][(int)(py + current_pos_y)]) return 1;
    }
    for (int j = 0; j < CAR_SIZE_Y; j++) {
        int i = CAR_SIZE_X*(j%2);
        float px = rotate_point_around_x((float) i, (float)j, rot, x, y);
        float py = rotate_point_around_y((float) i, (float)j, rot, x, y);
        if (collisions[(int)(px + current_pos_x)][(int)(py + current_pos_y)]) return 1;
    }

    return 0;
}

float rotate_point_around_x(float x, float y, float angle, float cx, float cy) {
    return (x - cx)*cosf(angle) - (y - cy)*sinf(angle);
}

float rotate_point_around_y(float x, float y, float angle, float cx, float cy) {
    return (x - cx)*sinf(angle) + (y - cy)*cosf(angle);
}

float cast_ray(float x, float y, float angle) {
    float dx = cosf(angle);
    float dy = sinf(angle);
    float dist = 0.0;
    while (!terrain[(int)(x + dist * dx)][(int)(y + dist * dy)]) {
        dist++;
    }
    return dist;
}

float cast_ray_x(float x, float y, float angle) {
    float dx = cosf(angle);
    float dy = sinf(angle);
    float dist = 0.0;
    while (!terrain[(int)(x + dist * dx)][(int)(y + dist * dy)]) {
        dist++;
    }
    return x + dist * dx;
}

float cast_ray_y(float x, float y, float angle) {
    float dx = cosf(angle);
    float dy = sinf(angle);
    float dist = 0.0;
    while (!terrain[(int)(x + dist * dx)][(int)(y + dist * dy)]) {
        dist++;
    }
    return y + dist * dy;
}

void generate_dist_grid(int terrain_dist[DISTANCE_RESOLUTION*BASE_GRID_X][DISTANCE_RESOLUTION*BASE_GRID_Y], int base[BASE_GRID_X][BASE_GRID_Y]) {
    for (int i = 0; i < (int)BASE_GRID_X; i++) {
        for (int j = 0; j < (int)BASE_GRID_Y; j++) {
            for (int k = 0; k < (int) DISTANCE_RESOLUTION*DISTANCE_RESOLUTION; k++) {
                terrain_dist[i*(int)DISTANCE_RESOLUTION + k%((int)DISTANCE_RESOLUTION)][j*(int)DISTANCE_RESOLUTION + (int)((float)k/(float)(DISTANCE_RESOLUTION))] = base[i][j];
            }
        }
    }
}
void generate_terrain(int terrain[BASE_GRID_X][GRID_SIZE_Y], int base[BASE_GRID_X][BASE_GRID_Y]) {
    float block_size_x = (float) GRID_SIZE_X / (float) BASE_GRID_X;
    float block_size_y = (float) GRID_SIZE_Y / (float) BASE_GRID_Y;
    for (int i = 0; i < GRID_SIZE_X; i++) {
        for (int j = 0; j < GRID_SIZE_Y; j++) {
            terrain[i][j] = base[(int)((float)i/block_size_x)][(int)((float)j/block_size_y)];
        }
    }
}
int coords_to_one(int x, int y, int width) {
    return x*width + y;
}
int one_to_coords_x(int n, int width) {
    return (int) ((float)n/(float)width);
}
int one_to_coords_y(int n, int width) {
    return n%width;
}

void generate_distances(int distances[DISTANCE_RESOLUTION*BASE_GRID_X*DISTANCE_RESOLUTION*BASE_GRID_Y], int dist_terrain[DISTANCE_RESOLUTION*BASE_GRID_X][DISTANCE_RESOLUTION*BASE_GRID_Y], int start_x, int start_y) {
    int dist_width = (int)DISTANCE_RESOLUTION*BASE_GRID_X;
    int distance_nb = (int)DISTANCE_RESOLUTION*BASE_GRID_X*DISTANCE_RESOLUTION*BASE_GRID_Y;
    int done_dists[(int)DISTANCE_RESOLUTION*BASE_GRID_X*DISTANCE_RESOLUTION*BASE_GRID_Y];
    int remaining_dists = -1;
    for (int i = 0; i < distance_nb; i++) {
        done_dists[i] = dist_terrain[one_to_coords_x(i, dist_width)][one_to_coords_y(i, dist_width)];
        distances[i] = MAX_DIST;
        remaining_dists += 1 - done_dists[i];
    }
    int dist_grid_x = (int)(((float)DISTANCE_RESOLUTION*BASE_GRID_X)*(float)start_x/((float)GRID_SIZE_X));
    int dist_grid_y = (int)(((float)DISTANCE_RESOLUTION*BASE_GRID_Y)*(float)start_y/((float)GRID_SIZE_Y));
    distances[coords_to_one(dist_grid_x, dist_grid_y, dist_width)] = 0;
    //int j = 0;
    while (remaining_dists > 0) {
        int min_dist_index = 0;
        int min_dist_value = MAX_DIST;
        for (int k = 0; k < distance_nb; k++) {
            if (!done_dists[k] && distances[k] < min_dist_value) {
                min_dist_index = k;
                min_dist_value = distances[k];
            }
        }
        //min dist index is set
        int vx = one_to_coords_x(min_dist_index, dist_width);
        int vy = one_to_coords_y(min_dist_index, dist_width);

        int alt = min_dist_value + 1;

        int ui = coords_to_one(vx + 1, vy, dist_width);

        if (!done_dists[ui]) {
            distances[ui] = alt;
        }
        ui = coords_to_one(vx - 1, vy, dist_width);
        if (!done_dists[ui]) {
            distances[ui] = alt;
        }
        ui = coords_to_one(vx, vy + 1, dist_width);
        if (!done_dists[ui]) {
            distances[ui] = alt;
        }
        ui = coords_to_one(vx, vy - 1, dist_width);
        if (!done_dists[ui]) {
            distances[ui] = alt;
        }
        done_dists[min_dist_index] = 1;
        remaining_dists--;
    }
}