import random
import struct

import pyglet
from pyglet.window import key
import moderngl


class Vec2:
    """ Razred za shranjevanje tock z x in y koordinato. """

    def __init__(self, x, y):
        self.x = x
        self.y = y    

    def get_tuple(self):
        return (self.x, self.y)

    def zero(self):
        self.x = 0
        self.y = 0
        return self.get_tuple()


class RGB:
    """ Razred za shranjevanje RGB komponent barv. Komponente so v intervalu [0, 1]. """

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def get_tuple(self):
        return (self.r, self.g, self.b)

    def random(self):
        self.r = random.random()
        self.g = random.random()
        self.b = random.random()
        return self.get_tuple()


class Fraktali(pyglet.window.Window):
    def __init__(self):
        super().__init__(1280, 720, resizable=True)

        self.iterations = 1000
        self.zoom = 1.0
        self.center = Vec2(0, 0)
        self.julia_c = Vec2(-0.925, -0.0021)

        self.rgb = RGB(1, 0, 0)

        self.sierpinski_levels = 8

        self._init_gl()

        self.key_handler = key.KeyStateHandler()
        self.push_handlers(self.key_handler)

        self.input_ready = 0
        self._SHARED_KEYS = [key.LEFT, key.RIGHT, key.UP, key.DOWN, key.Q, key.E, key.N, key.R, key.P, key._1, key._2, key._3]
        self._COORD_KEYS = [key.A, key.S, key.D, key.W]

        self._COORD_STEP = 0.01

    def _init_gl(self):
        self.ctx = moderngl.create_context()

        self._init_shader_programs()

        self.shader_to_idx = {
            'MANDELBROT': 0,
            'JULIA': 1,
            'SIERPINSKI': 2
        }

        self.idx_to_shader = {
            v : k for k, v in self.shader_to_idx.items()
        }

        self.shader_idx = 0

        self.prog = self.shader_programs[self.shader_idx]

        self.create_sierpinski_vao()

        self.quad_vbo = self.ctx.buffer(struct.pack('8f', 
            -1.0, -1.0,
            -1.0, 1.0,
            1.0, -1.0,
            1.0, 1.0
        ))
        self.quad_vao = self.ctx.simple_vertex_array(self.prog, self.quad_vbo, 'vert')

        self.set_uniform('w_width', self.width)
        self.set_uniform('w_height', self.height)

        self.set_uniform('iterations', self.iterations)
        self.set_uniform('center', self.center.get_tuple())
        self.set_uniform('zoom', self.zoom)
        self.set_uniform('rgb', self.rgb.get_tuple())

    def _init_shader_programs(self):
        DEFAULT_VERTEX_SHADER = '''
            #version 330

            in vec2 vert;

            uniform int w_width;
            uniform int w_height;

            void main() {
                gl_Position = vec4(vert, 0.0, 1.0);
            }
        '''

        SIERPINSKI_VERTEX_SHADER = '''
            #version 330

            in vec2 vert;

            uniform float zoom;
            uniform vec2 center;

            uniform int w_width;
            uniform int w_height;

            void main() {
                vec2 pos = vec2(vert + center);
                pos.y *= w_width / float(w_height);
                gl_Position = vec4(pos, 0.0, zoom);
            }
        '''

        self.shader_programs = [
            self.ctx.program(
                vertex_shader=DEFAULT_VERTEX_SHADER,
                # Mandelbrot
                fragment_shader='''
                        #version 330

                        out vec4 frag_color;

                        uniform vec3 rgb;

                        uniform int w_width;
                        uniform int w_height;

                        uniform int iterations;
                        uniform vec2 center;
                        uniform float zoom;

                        void main()
                        {
                            float aspect_ratio = w_width / float(w_height);
                            float set_width = 2.5f * aspect_ratio;

                            // pretvorba koordinat pikslov v kompleksna števila
                            vec2 c = vec2((gl_FragCoord.x / w_width - 0.5f) * set_width * zoom, 
                                        (gl_FragCoord.y / w_height - 0.5f) * 2.5f * zoom) 
                                        - vec2(center.x + 0.5f, center.y);
                            vec2 z = vec2(0.0f, 0.0f);

                            int i;
                            for (i = 0; i < iterations; i++) {
                                z = vec2(z.x * z.x - z.y * z.y, 2 * z.x * z.y) + c;
                                if (length(z) >= 2) break;
                            }

                            if (i == iterations)
                                frag_color = vec4(0, 0, 0, 1);
                            else
                                frag_color = vec4(rgb, 1) * cos(90 * (1 - i / float(iterations)));
                        }
                ''',
            ),

            self.ctx.program(
                vertex_shader=DEFAULT_VERTEX_SHADER,
                # Juliajev
                fragment_shader='''
                        #version 330

                        out vec4 frag_color;

                        uniform vec3 rgb;

                        uniform int w_width;
                        uniform int w_height;

                        uniform int iterations;
                        uniform vec2 center;
                        uniform float zoom;

                        uniform vec2 c;

                        void main()
                        {
                            float aspect_ratio = w_width / float(w_height);
                            float set_width = 2.5f * aspect_ratio;

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
                                frag_color = vec4(rgb, 1) * sin(180 * (i / float(iterations)));
                        }
                ''',
            ),

            self.ctx.program(
                vertex_shader=SIERPINSKI_VERTEX_SHADER,
                # Sierpinskov
                fragment_shader='''
                    #version 330

                    uniform vec3 rgb;
                    out vec4 frag;

                    void main()
                    {
                        frag = vec4(rgb, 1);
                    }
                '''
            )
        ]

    def create_sierpinski_vao(self):
        self.sierpinski_vbo = self.ctx.buffer(self._create_sierpinski_array())
        self.sierpinski_vao = self.ctx.simple_vertex_array(self.shader_programs[self.shader_to_idx['SIERPINSKI']], self.sierpinski_vbo, 'vert')

    def _create_sierpinski_array(self):
        vert_array = []

        self.add_sierpinski_vertices(vert_array, 0, Vec2(-0.5, -0.433013), Vec2(0.5, -0.433013), Vec2(0.0, 0.433013))

        # seznam je potrebno preoblikovati v obliko primerno za OpenGL
        return struct.pack('{}f'.format(len(vert_array)), *vert_array)

    def add_sierpinski_vertices(self, array, level, v1, v2, v3):
        """ Funkcija, ki rekurzivno dodaja tocke sierpinskovega trikotnika v seznam 'array'. Tocke so v obliki Vec2. """

        if level >= self.sierpinski_levels:
            array.extend((v1.x, v1.y, v2.x, v2.y, v3.x, v3.y))
            return

        self.add_sierpinski_vertices(array, level + 1, v1, Vec2((v1.x + v2.x) / 2, v2.y), Vec2((v1.x + v3.x) / 2, (v1.y + v3.y) / 2))
        self.add_sierpinski_vertices(array, level + 1, Vec2((v1.x + v2.x) / 2, v1.y), v2, Vec2((v2.x + v3.x) / 2, (v1.y + v3.y) / 2))
        self.add_sierpinski_vertices(array, level + 1, Vec2((v1.x + v3.x) / 2, (v1.y + v3.y) / 2), Vec2((v2.x + v3.x) / 2, (v1.y + v3.y) / 2), v3)

    def set_uniform(self, key, value):
        self.prog[key].value = value

    def get_current_fractal(self):
        return self.idx_to_shader[self.shader_idx]

    def next_fractal(self):
        """ Funkcija spremeni kateri fraktal je trenutno prikazan. """

        self.shader_idx = (self.shader_idx + 1) % len(self.shader_programs)

        self.prog = self.shader_programs[self.shader_idx]

        if (self.shader_idx != self.shader_to_idx["SIERPINSKI"]):
            self.quad_vao = self.ctx.simple_vertex_array(self.prog, self.quad_vbo, 'vert')

            self.set_uniform('iterations', self.iterations)
        
        self.set_uniform('w_width', self.width)
        self.set_uniform('w_height', self.height)

        self.set_uniform('center', self.center.zero())
        self.zoom = 1.0
        self.set_uniform('zoom', self.zoom)

        self.set_uniform('rgb', self.rgb.get_tuple())

        if self.get_current_fractal() == 'JULIA':
            self.set_uniform('c', self.julia_c.get_tuple())

    def print_debug(self):
        """ Funkcija izpise podatke o trenutnem fraktalu na standardni izhod. """

        trenutni_fraktal = self.idx_to_shader[self.shader_idx]
        print("Fraktal: {}".format(trenutni_fraktal))
        print("Povecava: {:.02f}".format(1 / self.zoom))
        if trenutni_fraktal == "SIERPINSKI":
            print("Stopnja: {}".format(self.sierpinski_levels))
        else:
            print("Iteracije: {}".format(self.iterations))
            if trenutni_fraktal == "JULIA":
                print("Julia c parameter: {:.05f} {} {:.05f}i".format(self.julia_c.x, '+' if self.julia_c.y > 0 else '', self.julia_c.y))
        print("Sredina: ({:.03f}, {:.03f})".format(self.center.x, self.center.y))
        print("RGB: {:.03f}, {:.03f}, {:.03f}".format(self.rgb.r, self.rgb.g, self.rgb.b))

    def on_key_press(self, symbol, modifiers):
        if symbol == key.N:
            return self.next_fractal()

        if symbol in self._SHARED_KEYS:
            if symbol == key.R:
                return self.set_uniform('rgb', self.rgb.random())
            if symbol == key.P:
                return self.print_debug()

            self.input_ready += 1
            if self.get_current_fractal() == "SIERPINSKI":
                if symbol == key.Q:
                    self.sierpinski_levels = max(0, self.sierpinski_levels - 1)
                    self.create_sierpinski_vao()
                elif symbol == key.E:
                    self.sierpinski_levels += 1
                    self.create_sierpinski_vao()
        elif symbol in self._COORD_KEYS:
            if (self.get_current_fractal() == "JULIA"):
                self.input_ready += 1

    def on_key_release(self, symbol, modifiers):
        self.input_ready = max(0, self.input_ready - 1)

    def handle_input(self):
        """ Funkcija se ustrezno odzove na vnose s tipkovnico. """

        if self.input_ready <= 0:
            return
        
        if self.key_handler[key.LEFT]:
            self.center.x += 0.05 * self.zoom
            self.set_uniform('center', self.center.get_tuple())
        if self.key_handler[key.RIGHT]:
            self.center.x -= 0.05 * self.zoom
            self.set_uniform('center', self.center.get_tuple())
        if self.key_handler[key.UP]:
            self.center.y -= 0.05 * self.zoom
            self.set_uniform('center', self.center.get_tuple())
        if self.key_handler[key.DOWN]:
            self.center.y += 0.05 * self.zoom
            self.set_uniform('center', self.center.get_tuple())

        if self.key_handler[key.Q] and self.get_current_fractal() != "SIERPINSKI":
            self.iterations = max(self.iterations - 50, 50)
            self.set_uniform('iterations', self.iterations)
        if self.key_handler[key.E] and self.get_current_fractal() != "SIERPINSKI":
            self.iterations = max(self.iterations + 50, 50)
            self.set_uniform('iterations', self.iterations)

        if self.key_handler[key.A]:
            if (self.get_current_fractal() == "JULIA"):
                self.julia_c.x -= self._COORD_STEP
                self.set_uniform('c', self.julia_c.get_tuple())
        if self.key_handler[key.D]:
            if (self.get_current_fractal() == "JULIA"):
                self.julia_c.x += self._COORD_STEP
                self.set_uniform('c', self.julia_c.get_tuple())
        if self.key_handler[key.W]:
            if (self.get_current_fractal() == "JULIA"):
                self.julia_c.y += self._COORD_STEP
                self.set_uniform('c', self.julia_c.get_tuple())
        if self.key_handler[key.S]:
            if (self.get_current_fractal() == "JULIA"):
                self.julia_c.y -= self._COORD_STEP
                self.set_uniform('c', self.julia_c.get_tuple())

        if self.key_handler[key._1]:
            self.rgb.r = self.rgb.r + 0.01 if self.rgb.r + 0.01 <= 1 else 0
            self.set_uniform('rgb', self.rgb.get_tuple())
        if self.key_handler[key._2]:
            self.rgb.g = self.rgb.g + 0.01 if self.rgb.g + 0.01 <= 1 else 0
            self.set_uniform('rgb', self.rgb.get_tuple())
        if self.key_handler[key._3]:
            self.rgb.b = self.rgb.b + 0.01 if self.rgb.b + 0.01 <= 1 else 0
            self.set_uniform('rgb', self.rgb.get_tuple())

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """ Funkcija spremeni povecavo ob vrtenju kolesa na miski. """

        if scroll_y > 0:
            self.zoom = self.zoom - 0.1 * self.zoom
            self.set_uniform('zoom', self.zoom)
        elif scroll_y < 0:
            self.zoom = self.zoom + 0.1 * self.zoom
            self.set_uniform('zoom', self.zoom)

    def on_resize(self, width, height):
        """ Funkcija ustrezno spremeni velikost prikazanega fraktala, ko se spremeni velikost okna. """

        super().on_resize(width, height)
        self.width = width
        self.height = height
        self.set_uniform('w_width', self.width)
        self.set_uniform('w_height', self.height)

    def on_draw(self):
        """ Funkcija osvezi sliko na zaslonu z ustreznim fraktalom. """

        self.clear()
        
        if (self.shader_to_idx["SIERPINSKI"] == self.shader_idx):
            self.sierpinski_vao.render(moderngl.TRIANGLES)
        else:
            self.quad_vao.render(moderngl.TRIANGLE_STRIP)

    def update(self, dt):
        self.handle_input()


if __name__ == '__main__':
    fraktali = Fraktali()
    pyglet.clock.schedule_interval(fraktali.update, 1 / 60.0)  # naj se program osvezi 60-krat na sekundo
    pyglet.app.run()
