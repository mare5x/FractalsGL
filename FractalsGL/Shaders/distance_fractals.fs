#version 330 core

out vec4 frag_color;

uniform int w_width;
uniform int w_height;

uniform int iterations;
uniform vec2 center;
uniform float zoom;


float calc_dist(vec2 c)
{
	vec2 z = vec2(0.0f, 0.0f);
	vec2 dz = vec2(0, 0);

	float len = 0;
	for (int i = 0; i < iterations; i++) {
		dz = 2 * vec2(dz.x * z.x - dz.y * z.y, dz.y * z.x + dz.x * z.y) + vec2(1, 0);
		z = vec2(z.x * z.x - z.y * z.y, 2 * z.x * z.y) + c;

		len = length(z);
		if (len >= 2048) break;
	}

	return sqrt(len / length(dz)) * 0.5f * log(len);
}


vec4 mandelbrot()
{
	float aspect_ratio = w_width / float(w_height);
	float set_width = 2.5f * aspect_ratio;

	vec2 c = vec2((gl_FragCoord.x / w_width - 0.5f) * set_width * zoom, 
				  (gl_FragCoord.y / w_height - 0.5f) * 2.5f * zoom) 
				  - center;

	float dist = calc_dist(c);

	if (dist <= 0)
		return vec4(0, 0, 0, 1);
	else
		return vec4(1, 1, 1, 1) * cos(pow(4 * dist / zoom, 0.2));
}


void main()
{
	frag_color = mandelbrot();
}