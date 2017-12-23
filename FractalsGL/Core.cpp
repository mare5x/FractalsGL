#include "Core.h"
#include "glm/gtc/matrix_transform.hpp"

#include <algorithm>


Core::Core(int w, int h)
	:width(w),
	height(h),
	quit_requested(false), render_requested(true),
	cur_fractal(F_MANDELBROT),
	iterations(2000),
	cam_zoom(1),
	cam_center(0.5f, 0),
	julia_c(0.0f, 0.0f),
	projection(1.0f),
	view(1.0f),
	model(1.0f),
	cur_event(),
	window(nullptr),
	context(nullptr),
	vao(0), vbo(0), vao_cube(0), vbo_cube(0), shaders(F__SIZE)
{
	if (!init())
		quit();
}

void Core::run()
{
	while (!quit_requested) {
		input();

		update();

		render();
	}
}

void Core::input()
{
	while (SDL_PollEvent(&cur_event)) {
		if (cur_event.type == SDL_QUIT) {
			quit_requested = true;
		}
		else {
			handle_input(cur_event);
		}
	}
}

void Core::update()
{
}

void Core::render()
{
	if (render_requested) {
		glClearColor(1, 1, 1, 1);
		if (cur_fractal == T_CUBE)
			glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
		else
			glClear(GL_COLOR_BUFFER_BIT);

		shaders[fractal_idx()].use();

		if (cur_fractal == T_CUBE) {
			glBindVertexArray(vao_cube);
			glBindBuffer(GL_ARRAY_BUFFER, vbo_cube);
			glDrawArrays(GL_TRIANGLES, 0, 36);
		}
		else {
			glBindVertexArray(vao);
			glBindBuffer(GL_ARRAY_BUFFER, vbo);
			glDrawArrays(GL_TRIANGLES, 0, 6);
		}

		SDL_GL_SwapWindow(window);
		
		render_requested = false;
	}
}

bool Core::init()
{
	if (SDL_Init(SDL_INIT_VIDEO) == 0) {
		SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE);
		SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);
		SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3);

		window = SDL_CreateWindow("OpenGL Fractals", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE);
		if (!window) {
			SDL_Log("CREATE WINDOW ERROR: %s", SDL_GetError());
			return false;
		}

		context = SDL_GL_CreateContext(window);
		if (!context) {
			SDL_Log("CREATE CONTEXT ERROR: %s", SDL_GetError());
			return false;
		}

		if (!gladLoadGLLoader(static_cast<GLADloadproc>(SDL_GL_GetProcAddress)))
			return false;

		glViewport(0, 0, width, height);

		return init_gl();
	}
	else {
		SDL_Log("INIT ERROR: %s", SDL_GetError());
		return false;
	}
}

bool Core::init_gl()
{
	projection = glm::perspective(glm::radians(45.0f), (float)width / (float)height, 0.1f, 100.0f);
	view = glm::translate(view, glm::vec3(0.0f, 0.0f, -3.0f));
	model = glm::rotate(model, glm::radians(30.0f), glm::vec3(0.5f, 1.0f, 0.0f));

	float vertices[] = {
		// pos (x, y, z)			
		-1.0f, 1.0f, 0.0f,
		-1.0f, -1.0f, 0.0f,
		1.0f, -1.0f, 0.0f,
		
		-1.0f, 1.0f, 0.0f,
		1.0f, -1.0f, 0.0f,
		1.0f, 1.0f, 0.0f
	};

	float cube_vertices[] = {
		-0.5f, -0.5f, -0.5f,
		0.5f, -0.5f, -0.5f,
		0.5f,  0.5f, -0.5f,
		0.5f,  0.5f, -0.5f,
		-0.5f,  0.5f, -0.5f,
		-0.5f, -0.5f, -0.5f,

		-0.5f, -0.5f,  0.5f,
		0.5f, -0.5f,  0.5f,
		0.5f,  0.5f,  0.5f,
		0.5f,  0.5f,  0.5f,
		-0.5f,  0.5f,  0.5f,
		-0.5f, -0.5f,  0.5f,

		-0.5f,  0.5f,  0.5f,
		-0.5f,  0.5f, -0.5f,
		-0.5f, -0.5f, -0.5f,
		-0.5f, -0.5f, -0.5f,
		-0.5f, -0.5f,  0.5f,
		-0.5f,  0.5f,  0.5f,

		0.5f,  0.5f,  0.5f,
		0.5f,  0.5f, -0.5f,
		0.5f, -0.5f, -0.5f,
		0.5f, -0.5f, -0.5f,
		0.5f, -0.5f,  0.5f,
		0.5f,  0.5f,  0.5f,

		-0.5f, -0.5f, -0.5f,
		0.5f, -0.5f, -0.5f,
		0.5f, -0.5f,  0.5f,
		0.5f, -0.5f,  0.5f,
		-0.5f, -0.5f,  0.5f,
		-0.5f, -0.5f, -0.5f,

		-0.5f,  0.5f, -0.5f,
		0.5f,  0.5f, -0.5f,
		0.5f,  0.5f,  0.5f,
		0.5f,  0.5f,  0.5f,
		-0.5f,  0.5f,  0.5f,
		-0.5f,  0.5f, -0.5f
	};

	glGenVertexArrays(1, &vao);
	glGenBuffers(1, &vbo);

	glBindVertexArray(vao);

	glBindBuffer(GL_ARRAY_BUFFER, vbo);
	glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void*)(0));
	glEnableVertexAttribArray(0);

	glGenVertexArrays(1, &vao_cube);
	glGenBuffers(1, &vbo_cube);

	glBindVertexArray(vao_cube);

	glBindBuffer(GL_ARRAY_BUFFER, vbo_cube);
	glBufferData(GL_ARRAY_BUFFER, sizeof(cube_vertices), cube_vertices, GL_STATIC_DRAW);

	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void*)(0));
	glEnableVertexAttribArray(0);

	shaders[fractal_idx(F_MANDELBROT)] = Shader("Shaders/vert_shader.vs", "Shaders/mandelbrot.fs");
	init_shader(F_MANDELBROT);

	shaders[fractal_idx(F_JULIA)] = Shader("Shaders/vert_shader.vs", "Shaders/julia.fs");
	init_shader(F_JULIA);

	shaders[fractal_idx(T_CUBE)] = Shader("Shaders/3d_vert_shader.vs", "Shaders/cube.fs");
	init_shader(T_CUBE);

	shaders[fractal_idx(T_RAYMARCHER)] = Shader("Shaders/vert_shader.vs", "Shaders/simple_raymarcher.fs");
	init_shader(T_RAYMARCHER);

	return true;
}

void Core::quit()
{
	glDeleteVertexArrays(1, &vao);
	glDeleteBuffers(1, &vbo);
	glDeleteVertexArrays(1, &vao_cube);
	glDeleteBuffers(1, &vbo_cube);

	SDL_GL_DeleteContext(context);
	context = nullptr;
	SDL_DestroyWindow(window);
	window = nullptr;

	SDL_Quit();
}

void Core::resize(int w, int h)
{
	width = w;
	height = h;
	glViewport(0, 0, width, height);
	
	for (Shader& shader : shaders) {
		shader.use();
		shader.setInt("w_width", width);
		shader.setInt("w_height", height);
	}
	render_requested = true;
}

void Core::handle_input(SDL_Event & e)
{
	if (e.type == SDL_KEYDOWN) {
		switch (e.key.keysym.sym)
		{
		case SDLK_LEFT:
			cam_center.x += 0.1f * cam_zoom;
			break;
		case SDLK_RIGHT:
			cam_center.x -= 0.1f * cam_zoom;
			break;
		case SDLK_UP:
			cam_center.y -= 0.1f * cam_zoom;
			break;
		case SDLK_DOWN:
			cam_center.y += 0.1f * cam_zoom;
			break;
		case SDLK_q:
			iterations = std::max(50, iterations - 50);
			break;
		case SDLK_e:
			iterations += 50;
			break;
		case SDLK_n:
			load_next_fractal();
			break;
		case SDLK_a:
			julia_c.x -= 0.05f;
			break;
		case SDLK_s:
			julia_c.x += 0.05f;
			break;
		case SDLK_d:
			julia_c.y -= 0.05f;
			break;
		case SDLK_f:
			julia_c.y += 0.05f;
			break;
		default:
			break;
		}

		size_t idx = fractal_idx();
		shaders[idx].setVec2("center", cam_center);
		shaders[idx].setInt("iterations", iterations);
		if (idx == fractal_idx(F_JULIA))
			shaders[idx].setVec2("c", julia_c);
		render_requested = true;
	}
	else if (e.type == SDL_MOUSEWHEEL) {
		if (e.wheel.y == 1)
			cam_zoom -= 0.1f * cam_zoom;
		else if (e.wheel.y == -1)
			cam_zoom += 0.1f * cam_zoom;

		shaders[fractal_idx()].setFloat("zoom", cam_zoom);
		render_requested = true;
	}
	else if (e.type == SDL_WINDOWEVENT && e.window.event == SDL_WINDOWEVENT_SIZE_CHANGED) {
		resize(e.window.data1, e.window.data2);
	}
}

void Core::init_shader(FRACTAL_TYPE type)
{
	Shader& shader = shaders[static_cast<size_t>(type)];
	shader.use();
	shader.setVec2("center", cam_center);
	shader.setFloat("zoom", cam_zoom);
	shader.setInt("w_width", width);
	shader.setInt("w_height", height);
	shader.setInt("iterations", iterations);
	if (type == F_JULIA)
		shader.setVec2("c", julia_c);
	else if (type == T_CUBE) {
		shader.setMat4("model", model);
		shader.setMat4("view", view);
		shader.setMat4("projection", projection);
	}
}

void Core::load_default_settings()
{
	iterations = 2000;
	cam_zoom = 1;
	cam_center = { 0.5f, 0 };
	julia_c = { 0.0f, 0.0f };
}

void Core::load_next_fractal()
{
	cur_fractal = static_cast<FRACTAL_TYPE>((static_cast<size_t>(cur_fractal) + 1) % F__SIZE);
	
	render_requested = true;

	load_default_settings();
	init_shader(cur_fractal);
	
	if (cur_fractal == T_CUBE)
		glEnable(GL_DEPTH_TEST);
	else
		glDisable(GL_DEPTH_TEST);
}
