/**************************************************************************************************/

#include "fitz-extension.h"

/**************************************************************************************************/

#include "mupdf/pdf.h"

#include <ft2build.h>
#include FT_FREETYPE_H
#include FT_ADVANCES_H

/* ********************************************************************************************** */

FILE *
fz_fopen(const char *filename, const char *mode)
{
  return fopen(filename, mode);
}

int
fz_fclose(FILE *file)
{
  return fclose(file);
}

/* ********************************************************************************************** */

int
font_is_bold(const fz_font *font)
{
  FT_Face face = font->ft_face;
  if (face && (face->style_flags & FT_STYLE_FLAG_BOLD))
    return 1;
  if (strstr(font->name, "Bold"))
    return 1;
  return 0;
}

int
font_is_italic(const fz_font *font)
{
  FT_Face face = font->ft_face;
  if (face && (face->style_flags & FT_STYLE_FLAG_ITALIC))
    return 1;
  if (strstr(font->name, "Italic") || strstr(font->name, "Oblique"))
    return 1;
  return 0;
}

/* ********************************************************************************************** */

/*
fz_text_span *
get_text_span(fz_text_line *line, unsigned int span_index)
{
  fz_text_span * span = line->first_span;
  size_t i = 0;
  while (i < span_index)
    {
      if (span)
	span = span->next;
      else
	return NULL;
      i += 1;
    }

  return span;
}
*/

/* ********************************************************************************************** */

// Helper for
// int fz_lookup_metadata(fz_context *ctx, fz_document *doc, const char *key, char *buf, int size);
int
meta(fz_context *ctx, fz_document *doc, const char *key, char *string, char *buffer, int buffer_size)
{
  *(char **)buffer = string;
  return fz_lookup_metadata(ctx, doc, key, buffer, buffer_size);
}

/* ********************************************************************************************** */

// Fixme: missing feature in mupdf/pdf.h
fz_buffer *
pdf_metadata(fz_context *ctx, fz_document *_doc)
{
  if (_doc) // Fixme: check document is a pdf!
    {
      pdf_document *doc = (pdf_document *)_doc;
      pdf_obj *catalog = pdf_dict_gets(ctx, pdf_trailer(ctx, doc), "Root");
      pdf_obj *metadata = pdf_dict_gets(ctx, catalog, "Metadata");
      if (metadata)
	{
	  fz_stream *stm = pdf_open_stream(ctx, doc, pdf_to_num(ctx, metadata), pdf_to_gen(ctx, metadata));
	  fz_buffer *buffer = fz_read_all(ctx, stm, 10240); // Fixme:
	  // fixme: fz_close(stm);
	  return buffer;
	}
    }
  return NULL;
}

/* ********************************************************************************************** */

#include <setjmp.h>
jmp_buf exception_buffer;
char *exception_message = NULL;

void
python_throw_exit_callback(char *message)
{
  exception_message = message;
  fz_longjmp(exception_buffer, 1);
}

void
init () {
  // fixme: fz_set_throw_exit_callback(python_throw_exit_callback);
}

fz_document *
open_document (fz_context * ctx, const char *filename) {
  if (! fz_setjmp(exception_buffer))
  {
    return fz_open_document(ctx, filename);
  }
  else // an exception raised
  {
    // PyErr_SetString(PyExc_NameError, exception_message);
    return NULL;
  }
}

/***************************************************************************************************
 * 
 * End
 * 
 **************************************************************************************************/
