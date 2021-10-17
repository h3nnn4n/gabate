#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "graphics.h"
#include "lelmark.h"
#include "other_window.h"
#include "overlay.h"
#include "tetris.h"
#include "types.h"

void draw_array(_cpu_info *cpu, uint16_t base, uint8_t offset, int x, int y, int r, int g, int b) {
    char text[512];
    text[0] = '\0';

    for (uint16_t addr = base; addr < base + offset; ++addr) {
        char text2[256];
        sprintf(text2, "%2x ", cpu->mem_controller.memory[addr]);
        strcat(text, text2);
    }

    draw_text_with_bg_overlay(text, x, y, r, g, b);
}

#pragma GCC diagnostic ignored "-Wunused-parameter"
void overlay_main(_cpu_info *cpu) {
#if 0
    char text[256];
    int posx = 0;
    int posy = 20;

    _best_piece best_piece = *(get_best_piece_pointer());

    best_piece.coord.x *= 4;
    best_piece.coord.y *= 4;

    draw_square_overlay(best_piece.coord.x + best_piece.blocks.a.x * 8*4 , best_piece.coord.y + best_piece.blocks.a.y * 8*4, 60 , 100, 255 );
    draw_square_overlay(best_piece.coord.x + best_piece.blocks.b.x * 8*4 , best_piece.coord.y + best_piece.blocks.b.y * 8*4, 60 , 100, 255 );
    draw_square_overlay(best_piece.coord.x + best_piece.blocks.c.x * 8*4 , best_piece.coord.y + best_piece.blocks.c.y * 8*4, 60 , 100, 255 );
    draw_square_overlay(best_piece.coord.x + best_piece.blocks.d.x * 8*4 , best_piece.coord.y + best_piece.blocks.d.y * 8*4,  0 ,   0, 255 );

    // Draws the centre of the piece
    /*int px = cpu->mem_controller.memory[0xc202];*/
    /*int py = cpu->mem_controller.memory[0xc201];*/
    /*draw_rectangle(px*4, py*4, 8*4, 8*4, 127, 127, 0);*/
    /*sprintf(text,"%2d %2d", px, py);*/
    /*draw_text(text, px * 4, py * 4, 255, 0, 0);*/

    // Draws the bottom rightmost block
    int px2 = cpu->mem_controller.memory[0xff92] - 8;
    int py2 = cpu->mem_controller.memory[0xff93] - 16;
    sprintf(text,"%2d %2d", px2, py2);
    /*draw_text_with_bg_overlay(text, (px2 + 4) * 4, py2 * 4, 0, 0, 255);*/
    draw_rectangle_overlay(px2*4, py2*4, 8*4, 8*4, 0, 255, 0);

    // mirror for `0xff92`
    int px3 = cpu->mem_controller.memory[0xffb3] - 8;
    int py3 = cpu->mem_controller.memory[0xffb2] - 16;
    sprintf(text,"%2d %2d", px3, py3);
    draw_rectangle_overlay(px3*4, py3*4, 8*4, 8*4, 0, 127, 127);
    /*draw_text(text, px3 * 4, py3 * 4, 0, 255, 255);*/


    posy += 20; draw_array(cpu, 0xc0a0, 3, posx, posy, 255, 255, 0); // Score
    posy += 20; draw_array(cpu, 0xc0a3, 8, posx, posy, 255, 255, 0); // FInished row pointers

    posy = 20; posx = 380;

    posy += 20; draw_array(cpu, 0xc822, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc832, 10, posx, posy, 255, 255, 0);*/
    posy += 20; draw_array(cpu, 0xc842, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc852, 10, posx, posy, 255, 255, 0);*/
    posy += 20; draw_array(cpu, 0xc862, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc872, 10, posx, posy, 255, 255, 0);*/
    posy += 20; draw_array(cpu, 0xc882, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc892, 10, posx, posy, 255, 255, 0);*/
    posy += 20; draw_array(cpu, 0xc8a2, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc8b2, 10, posx, posy, 255, 255, 0);*/
    posy += 20; draw_array(cpu, 0xc8c2, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc8d2, 10, posx, posy, 255, 255, 0);*/
    posy += 20; draw_array(cpu, 0xc8e2, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc8f2, 10, posx, posy, 255, 255, 0);*/

    posy += 20; draw_array(cpu, 0xc902, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc912, 10, posx, posy, 255, 255, 0);*/
    posy += 20; draw_array(cpu, 0xc922, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc932, 10, posx, posy, 255, 255, 0);*/
    posy += 20; draw_array(cpu, 0xc942, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc952, 10, posx, posy, 255, 255, 0);*/
    posy += 20; draw_array(cpu, 0xc962, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc972, 10, posx, posy, 255, 255, 0);*/
    posy += 20; draw_array(cpu, 0xc982, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc992, 10, posx, posy, 255, 255, 0);*/
    posy += 20; draw_array(cpu, 0xc9a2, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc9b2, 10, posx, posy, 255, 255, 0);*/
    posy += 20; draw_array(cpu, 0xc9c2, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc9d2, 10, posx, posy, 255, 255, 0);*/
    posy += 20; draw_array(cpu, 0xc9e2, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc9d2, 10, posx, posy, 255, 255, 0);*/
    posy += 20; draw_array(cpu, 0xca02, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xc912, 10, posx, posy, 255, 255, 0);*/
    posy += 20; draw_array(cpu, 0xca22, 10, posx, posy, 255, 255, 0);
  /*posy += 20; draw_array(cpu, 0xca32, 10, posx, posy, 255, 255, 0);*/
#endif
}
