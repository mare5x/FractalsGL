#version 330 core
layout (location = 0) in vec3 in_v_pos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 frag_pos;

void main()
{
	gl_Position = projection * view * model * vec4(in_v_pos, 1.0);
	frag_pos = vec3(model * vec4(in_v_pos, 1.0));
}