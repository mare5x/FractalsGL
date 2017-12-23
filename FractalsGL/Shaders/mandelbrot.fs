#version 330 core

in vec2 tex_pos;

out vec4 frag_color;

uniform sampler2D texture;

uniform int w_width;
uniform int w_height;

uniform int iterations;
uniform vec2 center;
uniform float zoom;

void main()
{
	float aspect_ratio = w_width / float(w_height);
	float set_width = 2.5f * aspect_ratio;

	vec2 c = vec2((gl_FragCoord.x / w_width - 0.5f) * set_width * zoom, 
				  (gl_FragCoord.y / w_height - 0.5f) * 2.5f * zoom) 
				  - center;
	vec2 z = vec2(0.0f, 0.0f);

	int i;
	for (i = 0; i < iterations; i++) {
		z = vec2(z.x * z.x - z.y * z.y, 2 * z.x * z.y) + c;
		if (length(z) >= 2) break;
	}

	if (i == iterations)
		frag_color = vec4(0, 0, 0, 1);
	else
		frag_color = vec4(1, 1, 1, 1) * cos(360 * (1 - i / float(iterations)));
}