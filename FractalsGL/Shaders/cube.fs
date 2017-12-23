#version 330 core

in vec3 frag_pos;

out vec4 frag_color;

uniform int w_width;
uniform int w_height;

void main()
{
	vec3 cam_pos = vec3(0, 0, -3);
	vec3 light_pos = vec3(1, 3, -5);

	vec3 norm = normalize(vec3(1, 0, 0));

	float diffuse = max(0, dot(norm, normalize(light_pos - frag_pos)));

	frag_color = vec4(1, 0, 0, 1) * diffuse;
}