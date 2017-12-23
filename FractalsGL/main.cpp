#include "Core.h"

const int WIDTH = 800;
const int HEIGHT = 600;


int main(int argc, char* argv[])
{
	Core core(WIDTH, HEIGHT);
	core.run();

	return 0;
}