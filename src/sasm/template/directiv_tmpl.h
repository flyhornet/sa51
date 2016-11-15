/*
 * This	file is generated from directiv.xml
 * by directiv.py; do not edit.
 */

#ifndef NASM_DIRECTIVES_H
#define NASM_DIRECTIVES_H

enum directives {
    $V
};

extern const char * const directives[$NV];
enum directives find_directive(const char *token);

#endif /* NASM_DIRECTIVES_H */