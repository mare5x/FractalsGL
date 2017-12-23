#version 330 core

out vec4 frag_color;

uniform int w_width;
uniform int w_height;

uniform int iterations;
uniform vec2 center;
uniform float zoom;

uniform vec2 c;

void main()
{
	float set_width = 2.5f * w_width / float(w_height);

	vec2 z = vec2((gl_FragCoord.x / w_width - 0.5f) * set_width * zoom, 
				  (gl_FragCoord.y / w_height - 0.5f) * 2.5f * zoom) 
				  - center;

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