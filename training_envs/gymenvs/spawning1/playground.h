#define GRID_SIZE_X 630
#define GRID_SIZE_Y 630
#define BASE_GRID_X 9
#define BASE_GRID_Y 9
#define DISTANCE_RESOLUTION 70
#define MAX_DIST 1000000

#define MAX_SPEED 10
#define STATE_HISTORY 1
#define STATE_SIZE 6

#define CAR_SIZE_X 25
#define CAR_SIZE_Y 14
#define WHEEL_SPACING REPLACE_WHEEL_SPACING
#define LID_RAY_NB 4
#define COLLIDE_REWARD 1200
#define MAX_TURN 6
#define MAX_LID_RAYS 360


#define HISTORY_MOD 16

void generate_dist_grid(int [DISTANCE_RESOLUTION*BASE_GRID_X][DISTANCE_RESOLUTION*BASE_GRID_Y], int [BASE_GRID_X][BASE_GRID_Y]);
void generate_terrain(int [GRID_SIZE_X][GRID_SIZE_Y], int [BASE_GRID_X][BASE_GRID_Y]);
void generate_distances(int [DISTANCE_RESOLUTION*BASE_GRID_X*DISTANCE_RESOLUTION*BASE_GRID_Y], int [DISTANCE_RESOLUTION*BASE_GRID_X][DISTANCE_RESOLUTION*BASE_GRID_Y], int, int);

void load_terrain_file(char *);

void add_car_collision_points(float, float, float);
void add_collision_point(int, int);
void reset_collision_points();
int is_collision(int, int);

void set_lid_ray_nb(int);
void set_lid_rays(float []);

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

void reset();
void lid_scan();
void set_state(float, float, float);
float step(float, float, float);
void set_step_data(float, float, float, float, float, int, int, int, int);

int get_reward(float, float);
void init();