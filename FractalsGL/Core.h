#pragma once

#include <vector>
#include <string>

#include "glad/glad.h"
#include "SDL.h"
#include "Shader.h"


class Core {
public:
	Core(int w, int h);
	~Core() { quit(); }

	void run();

	void input();
	void update();
	void render();
private:
	enum FRACTAL_TYPE {
		F_MANDELBROT, F_JULIA, T_CUBE, T_RAYMARCHER, F__SIZE
	};

	bool init();
	bool init_gl();
	void init_shader(FRACTAL_TYPE type);
	void load_default_settings();
	void quit();

	void resize(int w, int h);

	void handle_input(SDL_Event& e);

	void load_next_fractal();

	size_t fractal_idx() const { return static_cast<size_t>(cur_fractal); }
	size_t fractal_idx(const FRACTAL_TYPE& type) const { return static_cast<size_t>(type); }

	int width, height;

	bool quit_requested, render_requested;

	FRACTAL_TYPE cur_fractal;

	int iterations;
	float cam_zoom;
	glm::vec2 cam_center;
	glm::vec2 julia_c;

	glm::mat4 projection, view, model;

	SDL_Event cur_event;

	SDL_Window* window;
	SDL_GLContext context;

	GLuint vao, vbo, vao_cube, vbo_cube;
	std::vector<Shader> shaders;
};
