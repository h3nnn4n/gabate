/******************************************************************************
 * Copyright (C) 2017  Renan S. Silva                                         *
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

#include "feature_set.h"
#include "feature_functions.h"
#include "ff_controller.h"
#include "tetris.h"
#include "trainer.h"

#define STORE_FEATURE(value) get_current_cost()[ff_ctrl_next()] = (value)

void feature_set_basic() {
    STORE_FEATURE(complete_rows());

    if (cleaned_any_row()) {
        clear_lines();
    }

    STORE_FEATURE(holes());
    STORE_FEATURE(aggregate_height());
    STORE_FEATURE(surface_variance());
}

void feature_set_testing() {

    STORE_FEATURE(complete_rows());
    STORE_FEATURE(complete_rows_weighted());
    STORE_FEATURE(eroded_pieces());

    if (cleaned_any_row()) {
        clear_lines();
    }

    STORE_FEATURE(max_height());
    STORE_FEATURE(min_height());
    /*STORE_FEATURE(mean_column_height());*/
    /*STORE_FEATURE(max_mean_column_height());*/
    /*STORE_FEATURE(min_mean_column_height());*/
    STORE_FEATURE(holes());
    /*STORE_FEATURE(holes_vertical());*/
    /*STORE_FEATURE(mean_hole_depth());*/
    /*STORE_FEATURE(height_delta());*/
    STORE_FEATURE(well_cells());
    /*STORE_FEATURE(max_well_depth());*/
    /*STORE_FEATURE(number_of_wells());*/
    /*STORE_FEATURE(total_well_depth());*/
    /*STORE_FEATURE(well_cells_weigthed());*/
    STORE_FEATURE(lock_heigth());
    STORE_FEATURE(aggregate_height());
    /*STORE_FEATURE(blocks());*/
    STORE_FEATURE(blocks_weighted());

    STORE_FEATURE(horizontal_roughness());
    STORE_FEATURE(vertical_roughness());

    /*STORE_FEATURE(highest_hole());*/
    /*STORE_FEATURE(blocks_above_highest_hole());*/
    STORE_FEATURE(potential_rows());
    STORE_FEATURE(surface_variance());
    STORE_FEATURE(rows_with_a_hole());
    /*STORE_FEATURE(hole_depth());*/
    STORE_FEATURE(pattern_diversity());
    /*STORE_FEATURE(free_blocks());*/

    /*STORE_FEATURE(blocks_above_highest_hole_w());*/
    /*STORE_FEATURE(horizontal_roughness_w());*/
    /*STORE_FEATURE(vertical_roughness_w());*/

    /*for (int i = 0; i < 10; ++i) {*/
    /*brain->population[brain->current].cost[ff_ctrl_next()]  = column_height(i);*/
    /*}*/

    /*for (int i = 0; i < 9; ++i) {*/
    /*brain->population[brain->current].cost[ff_ctrl_next()]  = height_difference(i);*/
    /*}*/
}

void feature_set_FBDP() {

    if (cleaned_any_row()) {
        clear_lines();
    }

    STORE_FEATURE(holes());         // 1
    STORE_FEATURE(highest_cell());  // 6
}

void feature_set_NDP() {

    if (cleaned_any_row()) {
        clear_lines();
    }

    STORE_FEATURE(holes());
    STORE_FEATURE(highest_cell());

    for (int i = 0; i < 10; ++i) {
        STORE_FEATURE(column_height(i));
    }

    for (int i = 0; i < 9; ++i) {
        STORE_FEATURE(height_difference(i));
    }
}

void feature_set_KBR() {

    if (cleaned_any_row()) {
        clear_lines();
    }

    STORE_FEATURE(holes());         // 1
    STORE_FEATURE(highest_cell());  // 6

    for (int i = 0; i < 10; ++i) {
        STORE_FEATURE(column_height(i));
    }

    for (int i = 0; i < 9; ++i) {
        STORE_FEATURE(height_difference(i));
    }
    STORE_FEATURE(mean_column_height());      // 3
    STORE_FEATURE(min_height());              // 2
    STORE_FEATURE(max_mean_column_height());  // 4
    STORE_FEATURE(min_mean_column_height());  // 5
    STORE_FEATURE(mean_hole_depth());         // 8
    STORE_FEATURE(well_cells());              // 16
}

void feature_set_CMA() {

    STORE_FEATURE(complete_rows());  // 10
    STORE_FEATURE(eroded_pieces());  // 32

    if (cleaned_any_row()) {
        clear_lines();
    }

    STORE_FEATURE(holes());            // 6
    STORE_FEATURE(blocks_weighted());  // 21
    STORE_FEATURE(well_cells());       // 16
    STORE_FEATURE(blocks());           // 20
    STORE_FEATURE(lock_heigth());      // 18

    STORE_FEATURE(horizontal_roughness());  // 22
    STORE_FEATURE(vertical_roughness());    // 24

    STORE_FEATURE(well_cells_weigthed());  // 17
    STORE_FEATURE(hole_depth());           // 34

    STORE_FEATURE(rows_with_a_hole());   // 33
    STORE_FEATURE(pattern_diversity());  // 35
}

void feature_set_HA2() {

    STORE_FEATURE(complete_rows());  // 10
    STORE_FEATURE(complete_rows_weighted());
    STORE_FEATURE(eroded_pieces());  // 32

    if (cleaned_any_row()) {
        clear_lines();
    }

    STORE_FEATURE(holes());           // 1
    STORE_FEATURE(highest_cell());    // 6
    STORE_FEATURE(holes_vertical());  // 7
    STORE_FEATURE(height_delta());    // 12
    STORE_FEATURE(max_well_depth());  // 14
    STORE_FEATURE(well_cells());      // 13
    STORE_FEATURE(lock_heigth());     // 18

    STORE_FEATURE(blocks());                // 20
    STORE_FEATURE(blocks_weighted());       // 21
    STORE_FEATURE(horizontal_roughness());  // 22
    STORE_FEATURE(vertical_roughness());    // 24
    STORE_FEATURE(horizontal_roughness_w());
    STORE_FEATURE(vertical_roughness_w());

    STORE_FEATURE(highest_hole());               // 26
    STORE_FEATURE(blocks_above_highest_hole());  // 27
    STORE_FEATURE(potential_rows());             // 29
    STORE_FEATURE(surface_variance());           // 30
    STORE_FEATURE(rows_with_a_hole());           // 33
    STORE_FEATURE(hole_depth());                 // 34
    STORE_FEATURE(pattern_diversity());          // 35
    STORE_FEATURE(burried_cells());
}

void feature_set_HA() {

    STORE_FEATURE(complete_rows());  // 10
    STORE_FEATURE(eroded_pieces());  // 32

    if (cleaned_any_row()) {
        clear_lines();
    }

    STORE_FEATURE(holes());           // 1
    STORE_FEATURE(highest_cell());    // 6
    STORE_FEATURE(holes_vertical());  // 7
    STORE_FEATURE(height_delta());    // 12
    STORE_FEATURE(max_well_depth());  // 14
    STORE_FEATURE(well_cells());      // 13
    STORE_FEATURE(lock_heigth());     // 18

    STORE_FEATURE(blocks());                // 20
    STORE_FEATURE(blocks_weighted());       // 21
    STORE_FEATURE(horizontal_roughness());  // 22
    STORE_FEATURE(vertical_roughness());    // 24

    STORE_FEATURE(highest_hole());               // 26
    STORE_FEATURE(blocks_above_highest_hole());  // 27
    STORE_FEATURE(potential_rows());             // 29
    STORE_FEATURE(surface_variance());           // 30
    STORE_FEATURE(rows_with_a_hole());           // 33
    STORE_FEATURE(hole_depth());                 // 34
}

void feature_set_LELmark() {

    STORE_FEATURE(complete_rows());
    STORE_FEATURE(complete_rows_weighted());

    if (cleaned_any_row()) {
        clear_lines();
    }

    STORE_FEATURE(aggregate_height());
    STORE_FEATURE(covered_cells());
    STORE_FEATURE(surface_variance());
    STORE_FEATURE(well_cells());
    STORE_FEATURE(lock_heigth());
    STORE_FEATURE(burried_cells());
    STORE_FEATURE(highest_cell());
    STORE_FEATURE(height_delta());
    STORE_FEATURE(vertical_roughness());
    STORE_FEATURE(horizontal_roughness());
    STORE_FEATURE(vertical_roughness_w());
    STORE_FEATURE(horizontal_roughness_w());
}

void feature_set_ALL() {

    STORE_FEATURE(complete_rows());
    STORE_FEATURE(complete_rows_weighted());
    STORE_FEATURE(eroded_pieces());

    if (cleaned_any_row()) {
        clear_lines();
    }

    STORE_FEATURE(max_height());
    STORE_FEATURE(min_height());
    STORE_FEATURE(mean_column_height());
    STORE_FEATURE(max_mean_column_height());
    STORE_FEATURE(min_mean_column_height());
    STORE_FEATURE(holes());
    STORE_FEATURE(holes_vertical());
    STORE_FEATURE(mean_hole_depth());
    STORE_FEATURE(height_delta());
    STORE_FEATURE(well_cells());
    STORE_FEATURE(max_well_depth());
    STORE_FEATURE(number_of_wells());
    STORE_FEATURE(total_well_depth());
    STORE_FEATURE(well_cells_weigthed());
    STORE_FEATURE(lock_heigth());
    STORE_FEATURE(aggregate_height());
    STORE_FEATURE(blocks());
    STORE_FEATURE(blocks_weighted());

    STORE_FEATURE(horizontal_roughness());
    STORE_FEATURE(vertical_roughness());

    STORE_FEATURE(highest_hole());
    STORE_FEATURE(blocks_above_highest_hole());
    STORE_FEATURE(potential_rows());
    STORE_FEATURE(surface_variance());
    STORE_FEATURE(rows_with_a_hole());
    STORE_FEATURE(hole_depth());
    STORE_FEATURE(pattern_diversity());
    STORE_FEATURE(free_blocks());

    STORE_FEATURE(blocks_above_highest_hole_w());
    STORE_FEATURE(horizontal_roughness_w());
    STORE_FEATURE(vertical_roughness_w());
}
