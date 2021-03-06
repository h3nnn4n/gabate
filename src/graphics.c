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

#include "graphics.h"
#include "overlay.h"
#include "types.h"

#include "file_control.h"
#include "other_window.h"
#include "rev.h"

/*#define __use_sdl*/

/*#define __save_frames*/
/*#define __render_window*/

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

void      flip_screen(_cpu_info *cpu) {}
void      sdl_init() {}
void      input_update(_cpu_info *cpu) {}
void      sdl_quit() {}
uint32_t *get_frame_buffer() { return NULL; }
void      draw_rectangle_overlay(int x, int y, int x2, int y2, int r, int g, int b) {}
void      draw_text_overlay(char *text, int x, int y, int r, int g, int b) {}
void      draw_text_with_bg_overlay(char *text, int x, int y, int r, int g, int b) {}

#endif
