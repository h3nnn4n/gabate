/******************************************************************************
 * Copyright (C) 2016  Renan S. Silva                                         *
 *                                                                            *
 * This software is provided 'as-is', without any express or implied          *
 * warranty. In no event will the authors be held liable for any damages      *
 * arising from the use of this software.                                     *
 *                                                                            *
 * Permission is granted to anyone to use this software for any purpose,      *
 * including commercial applications, and to alter it and redistribute it     *
 * freely, subject to the following restrictions:                             *
 *                                                                            *
 * 1. The origin of this software must not be misrepresented; you must not    *
 *    claim that you wrote the original software. If you use this software    *
 *    in a product, an acknowledgment in the product documentation would be   *
 *    appreciated but is not required.                                        *
 * 2. Altered source versions must be plainly marked as such, and must not be *
 *    misrepresented as being the original software.                          *
 * 3. This notice may not be removed or altered from any source distribution. *
 ******************************************************************************/
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>

#include "graphics.h"
#include "overlay.h"
#include "types.h"

#include "file_control.h"
#include "other_window.h"
#include "rev.h"
#include "settings.h"

/*#define __use_sdl*/

#define __save_png_frames
/*#define __render_window*/

#ifdef __save_png_frames
#include <png.h>
#include <errno.h>

static uint32_t frame_counter = 0;

void create_output_directory() {
    struct stat st = {0};

    char path[256];
    snprintf(path, sizeof(path), "output/%s/", get_agent_config()->run_id);
    if (stat(path, &st) == -1) {
        mkdir(path, 0755);
    }
}

void write_png_file(const char* filename, uint32_t* buffer, int width, int height) {
    FILE* fp = fopen(filename, "wb");
    if (!fp) return;

    png_structp png = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
    if (!png) {
        fclose(fp);
        return;
    }

    png_infop info = png_create_info_struct(png);
    if (!info) {
        png_destroy_write_struct(&png, NULL);
        fclose(fp);
        return;
    }

    if (setjmp(png_jmpbuf(png))) {
        png_destroy_write_struct(&png, &info);
        fclose(fp);
        return;
    }

    png_init_io(png, fp);
    png_set_IHDR(png, info, width, height, 8, PNG_COLOR_TYPE_RGB, PNG_INTERLACE_NONE,
                 PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT);
    png_write_info(png, info);

    png_bytep row = malloc(3 * width * sizeof(png_byte));
    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            uint32_t pixel = buffer[y * width + x];
            row[x * 3 + 0] = (pixel >> 16) & 0xFF;
            row[x * 3 + 1] = (pixel >> 8) & 0xFF;
            row[x * 3 + 2] = pixel & 0xFF;
        }
        png_write_row(png, row);
    }

    free(row);
    png_write_end(png, NULL);
    png_destroy_write_struct(&png, &info);
    fclose(fp);
}
#endif

#ifdef __use_sdl

#include "SDL.h"
#include "SDL_render.h"
#include "SDL_ttf.h"
#include "SDL_video.h"

#ifdef __render_window
static SDL_Window *window;
#endif

static SDL_Renderer *renderer;
static SDL_Texture * bitmap;
static TTF_Font *    font;
static uint32_t *    pixels;
static int           screenx = 160;
static int           screeny = 144;

#define BYTE_TO_BINARY_PATTERN "%c%c%c%c%c%c%c%c"
#define BYTE_TO_BINARY(byte)                                                                                           \
    (byte & 0x80 ? '1' : '0'), (byte & 0x40 ? '1' : '0'), (byte & 0x20 ? '1' : '0'), (byte & 0x10 ? '1' : '0'),        \
        (byte & 0x08 ? '1' : '0'), (byte & 0x04 ? '1' : '0'), (byte & 0x02 ? '1' : '0'), (byte & 0x01 ? '1' : '0')

uint32_t *get_frame_buffer() { return pixels; }

void sdl_init() {
    SDL_Init(SDL_INIT_VIDEO);
    TTF_Init();

#ifdef __render_window
    window = SDL_CreateWindow("here comes dat gameboi - LELmark edition", SDL_WINDOWPOS_CENTERED,
                              SDL_WINDOWPOS_CENTERED, screenx * 4, screeny * 4, 0);

    renderer = SDL_CreateRenderer(window, -1, 0);
#endif

    bitmap = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGB888, SDL_TEXTUREACCESS_STREAMING, screenx, screeny);
    pixels = malloc(sizeof(uint32_t) * screenx * screeny);
    SDL_RenderSetScale(renderer, 4, 4);

    memset(pixels, 255, screenx * screeny * sizeof(uint32_t));

    SDL_UpdateTexture(bitmap, NULL, pixels, screenx * sizeof(uint32_t));

    font = TTF_OpenFont("inconsolata.ttf", 18);
}

void flip_screen(_cpu_info *cpu) {
#ifdef __save_png_frames
    static int output_dir_created = 0;
    if (!output_dir_created) {
        create_output_directory();
        output_dir_created = 1;
    }

    char filename[256];
    sprintf(filename, "output/frame_%06d.png", frame_counter);
    frame_counter++;

    write_png_file(filename, pixels, screenx, screeny);
#endif

#ifdef __save_frames
    if (can_write_file_control()) {
        char name[256];
        sprintf(name, "frame_%016d_%016d.bmp", get_seed_file_control(), get_frame_number_file_control());

        bump_file_control();

        SDL_Surface *surf =
            SDL_CreateRGBSurfaceFrom(pixels, screenx, screeny, 32, screenx * sizeof(uint32_t), 0, 0, 0, 0);
        if (surf == NULL) {
            fprintf(stderr, "Null pointer at SDL_Surface\n");
            exit(-1);
        }

        SDL_SaveBMP(surf, name);

        SDL_FreeSurface(surf);
    }
#endif

#ifdef __render_window
    SDL_RenderClear(renderer);
    SDL_RenderCopy(renderer, bitmap, NULL, NULL);

    SDL_RenderSetScale(renderer, 1, 1);
    overlay_main(cpu);
    SDL_RenderSetScale(renderer, 4, 4);

    SDL_RenderPresent(renderer);

    SDL_UpdateTexture(bitmap, NULL, pixels, screenx * sizeof(uint32_t));
#endif
}

void draw_rectangle_overlay(int x, int y, int x2, int y2, int r, int g, int b) {
    SDL_SetRenderDrawColor(renderer, r, g, b, 0);
    SDL_Rect dstrect = {x, y, x2, y2};
    SDL_RenderFillRect(renderer, &dstrect);
}

void draw_square_overlay(int x, int y, int r, int g, int b) {
    int size = 1;
    int x2   = x / size;
    int y2   = y / size;
    int w2   = 8 * 4 / size;
    SDL_SetRenderDrawColor(renderer, r, g, b, 0);
    SDL_Rect dstrect = {x2, y2, w2, w2};
    SDL_RenderFillRect(renderer, &dstrect);
}

void draw_text_with_bg_overlay(char *text, int x, int y, int r, int g, int b) {
    int texW = 0;
    int texH = 0;

    SDL_Color    color   = {r, g, b, 0};
    SDL_Surface *surface = TTF_RenderText_Solid(font, text, color);
    SDL_Texture *texture = SDL_CreateTextureFromSurface(renderer, surface);

    SDL_QueryTexture(texture, NULL, NULL, &texW, &texH);
    /*printf("%d %d\n", texW, texH);*/
    SDL_Rect dstrect = {x, y, texW, texH};

    draw_rectangle_overlay(x, y, texW, texH, 0, 0, 0);

    SDL_RenderCopy(renderer, texture, NULL, &dstrect);

    SDL_DestroyTexture(texture);
    SDL_FreeSurface(surface);
}

void draw_text_overlay(char *text, int x, int y, int r, int g, int b) {
    int texW = 0;
    int texH = 0;

    SDL_Color    color   = {r, g, b, 0};
    SDL_Surface *surface = TTF_RenderText_Solid(font, text, color);
    SDL_Texture *texture = SDL_CreateTextureFromSurface(renderer, surface);

    SDL_QueryTexture(texture, NULL, NULL, &texW, &texH);
    SDL_Rect dstrect = {x, y, texW, texH};

    SDL_RenderCopy(renderer, texture, NULL, &dstrect);

    SDL_DestroyTexture(texture);
    SDL_FreeSurface(surface);
}

void input_update(_cpu_info *cpu) {
    SDL_Event ev;

    // Input documentation from: http://computerarcheology.com/Arcade/SpaceInvaders/Hardware.html
    while (SDL_PollEvent(&ev)) {
        switch (ev.type) {
            case SDL_KEYDOWN:
                switch (ev.key.keysym.sym) {
                    case SDLK_t: mem_find_mark_equal(); break;
                    case SDLK_u: mem_find_mark_diff(); break;
                    case SDLK_i: mem_find_mark_exact(); break;
                    case SDLK_y: mem_find_start(); break;
                    case SDLK_z: cpu->joystick.button_a = 0; break;
                    case SDLK_x: cpu->joystick.button_b = 0; break;
                    case SDLK_a: cpu->joystick.button_select = 0; break;
                    case SDLK_s: cpu->joystick.button_start = 0; break;
                    case SDLK_LEFT: cpu->joystick.button_left = 0; break;
                    case SDLK_RIGHT: cpu->joystick.button_right = 0; break;
                    case SDLK_DOWN: cpu->joystick.button_down = 0; break;
                    case SDLK_UP: cpu->joystick.button_up = 0; break;
                    default: break;
                }
                break;
            case SDL_KEYUP:
                switch (ev.key.keysym.sym) {
                    case SDLK_z: cpu->joystick.button_a = 1; break;
                    case SDLK_x: cpu->joystick.button_b = 1; break;
                    case SDLK_a: cpu->joystick.button_select = 1; break;
                    case SDLK_s: cpu->joystick.button_start = 1; break;
                    case SDLK_LEFT: cpu->joystick.button_left = 1; break;
                    case SDLK_RIGHT: cpu->joystick.button_right = 1; break;
                    case SDLK_DOWN: cpu->joystick.button_down = 1; break;
                    case SDLK_UP: cpu->joystick.button_up = 1; break;
                    default: break;
                }
                break;
            case SDL_WINDOWEVENT_CLOSE:
            case SDL_QUIT:
                printf("QUIT!\n");
                exit(0);
                break;
            default:
                /*cpu->portin0 = 0x0e;*/
                /*cpu->portin1 = 0x08;*/
                /*cpu->portin2 = 0x00;*/
                break;
        }
    }
    /*printf(BYTE_TO_BINARY_PATTERN"\n", BYTE_TO_BINARY(cpu->portin1));*/
}

void sdl_quit() { SDL_Quit(); }

#else

#pragma GCC diagnostic ignored "-Wunused-parameter"

static uint32_t *headless_buffer;
static int headless_screenx = 160;
static int headless_screeny = 144;

void flip_screen(_cpu_info *cpu) {
#ifdef __save_png_frames
    if (headless_buffer) {
        char filename[256];
        sprintf(filename, "output/frame_%06d.png", frame_counter);
        frame_counter++;

        write_png_file(filename, headless_buffer, headless_screenx, headless_screeny);
    }
#endif
}

void sdl_init() {
#ifdef __save_png_frames
    if (get_agent_config()->capture_output) {
        headless_buffer = malloc(sizeof(uint32_t) * headless_screenx * headless_screeny);
        memset(headless_buffer, 0, headless_screenx * headless_screeny * sizeof(uint32_t));
        create_output_directory();
    }
#endif
}

void      input_update(_cpu_info *cpu) {}

void sdl_quit() {
#ifdef __save_png_frames
    if (headless_buffer) {
        free(headless_buffer);
        headless_buffer = NULL;
    }
#endif
}

uint32_t *get_frame_buffer() {
#ifdef __save_png_frames
    return headless_buffer;
#else
    return NULL;
#endif
}

void      draw_rectangle_overlay(int x, int y, int x2, int y2, int r, int g, int b) {}
void      draw_text_overlay(char *text, int x, int y, int r, int g, int b) {}
void      draw_text_with_bg_overlay(char *text, int x, int y, int r, int g, int b) {}

#endif
