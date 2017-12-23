#version 330 core

out vec4 frag_color;

uniform int w_width;
uniform int w_height;

const int MAX_STEPS = 32;
const float MIN_DIST = 0.001;
const float MAX_DIST = 100;

const vec3 light_pos = vec3(3, 3, -4);


float tetrahedron_sfd(vec3 pos)
{
	vec3 a = vec3(-1, -1, -1);
	vec3 b = vec3(1, -1, -1);
	vec3 c = vec3(0, -1, 1);
	vec3 d = vec3(0, 1, 0);

	return min(length(pos - a), min(length(pos - b), min(length(pos - c), length(pos - d))));
}


float cube_sfd(vec3 pos, vec3 dimensions)
{
	vec3 d = abs(pos) - dimensions;
	return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
}


float cross_sfd(vec3 pos)
{
	float da = cube_sfd(pos.xyz, vec3(500,1.0,1.0));
	float db = cube_sfd(pos.yzx, vec3(1.0,500,1.0));
	float dc = cube_sfd(pos.zxy, vec3(1.0,1.0,500));
	return min(da, min(db, dc));
}


float sphere_sfd(vec3 pos, vec3 sphere_center, float radius)
{
	return length(pos - sphere_center) - radius;
}


// http://www.iquilezles.org/www/articles/menger/menger.htm
float menger_sponge_dist(vec3 pos)
{
	float d = cube_sfd(pos, vec3(1));

	float s = 1.0;
	for (int m = 0; m < 3; m++) {
		vec3 a = mod(pos * s, 2.0) - 1.0;
		s *= 3.0;
		vec3 r = 1.0 - 3.0 * abs(a);

		float c = cross_sfd(r) / s;
		d = max(d, c);
	}

	return d;
}


float world_sfd(vec3 pos)
{
	//return sphere_sfd(pos, vec3(0, 0, 0), 1);
	//return tetrahedron_sfd(pos);
	//return cube_sfd(pos);
	return menger_sponge_dist(pos);
}


float in_mandelbox(vec3 pos)
{
	const int ITERS = 15;
	vec3 z = vec3(0);
	for (int i = 0; i < ITERS; i++) {
		if (z.x > 1) z.x = 2 - z.x;
		else if (z.x < -1) z.x = -2 - z.x;
		
		if (z.y > 1) z.y = 2 - z.y;
		else if (z.y < -1) z.y = -2 - z.y;
		
		if (z.z > 1) z.z = 2 - z.z;
		else if (z.z < -1) z.z = -2 - z.z;
		
		float len = length(z);
		if (len > 2) return i / float(ITERS);

		if (len < 0.5) z *= 4;
		else if (len < 1) z = z / (len * len);

		z = z * -1.5 + pos;
	}
	return 1;
}


vec3 calc_normal(vec3 pos)
{
	vec3 eps = vec3(0.01, 0, 0);

	float dx = world_sfd(pos + eps.xyy) - world_sfd(pos - eps.xyy);
	float dy = world_sfd(pos + eps.yxy) - world_sfd(pos - eps.yxy);
	float dz = world_sfd(pos + eps.yyx) - world_sfd(pos - eps.yyx);

	return normalize(vec3(dx, dy, dz));
}


vec3 ray_march(vec3 ray_origin, vec3 ray_direction)
{
	vec3 dir = normalize(ray_direction);
	float dist = 0;
	for (int i = 0; i < MAX_STEPS; i++) {
		vec3 cur_pos = ray_origin + dir * dist;
		float cur_dist = world_sfd(cur_pos);

		if (cur_dist <= MIN_DIST) {
			vec3 normal = calc_normal(cur_pos);
			float diffuse = max(0, dot(normal, normalize(light_pos - cur_pos)));
			return vec3(1, 0, 0) * (diffuse + 0.1);
		} else if (cur_dist >= MAX_DIST) {
			return vec3(0, 0, 0);
		}
		dist += cur_dist;
	}

	return vec3(0, 0, 0);
}


vec3 ray_march_mandelbox(vec3 ray_origin, vec3 ray_direction)
{
	vec3 dir = normalize(ray_direction);
	float dist = 0;
	float res = 0, prev_res = 0;
	for (int i = 0; i < 1000; i++) {
		vec3 cur_pos = ray_origin + dir * dist;
		res = in_mandelbox(cur_pos);
		if (res == 1) {
			return vec3(1, 0, 0);
		}

		if (res < prev_res)
			return vec3(1, 0, 0) * res;
		
		prev_res = res;

		dist += 0.01;
	}
	return vec3(1, 1, 1) * res;
}


/**
 * Return a transform matrix that will transform a ray from view space
 * to world coordinates, given the eye point, the camera target, and an up vector.
 *
 * This assumes that the center of the camera is aligned with the negative z axis in
 * view space when calculating the ray marching direction. See rayDirection.
 */
mat4 viewMatrix(vec3 eye, vec3 center, vec3 up) {
    // Based on gluLookAt man page
    vec3 f = normalize(center - eye);
    vec3 s = normalize(cross(f, up));
    vec3 u = cross(s, f);
    return mat4(
        vec4(s, 0.0),
        vec4(u, 0.0),
        vec4(-f, 0.0),
        vec4(0.0, 0.0, 0.0, 1)
    );
}


void main()
{
	float aspect_ratio = w_width / float(w_height);

	vec3 cam_pos = vec3(7, 6, -3);

	mat4 world_view = viewMatrix(cam_pos, vec3(0), vec3(0, 1, 0));  // gluLookAt

	vec3 ray_origin = cam_pos;
	vec3 rd = vec3((gl_FragCoord.x / w_width - 0.5) * aspect_ratio,
				   (gl_FragCoord.y / w_height - 0.5), 
				   -2.0);  // has to be negative ?!?!

	vec3 ray_direction = (world_view * vec4(normalize(rd), 0)).xyz;

	vec3 color = ray_march(ray_origin, ray_direction);
	
	frag_color = vec4(color, 1.0);
}
