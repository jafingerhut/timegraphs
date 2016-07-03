/*
 * gawcolor.c - color functions
 *   GTK interface to Gaw
 * 
 * include LICENSE
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <stdio.h>
#include <string.h>
#include <math.h>
#include <sys/stat.h>

#include <gtk/gtk.h>

#include <duprintf.h>
#include <gaw.h>
 
#ifdef TRACE_MEM
#include <tracemem.h>
#endif


void ac_color_rgba_str_set(char **valp, GdkRGBA *rgba )
{
   char *colorspec = gdk_rgba_to_string(rgba);
   
   msg_dbg ("colorspec: %s", colorspec);
   app_dup_str( valp, colorspec );
}

static void ac_color_rgba_ary_set(ArrayStr *ary, GdkRGBA *color, int index )
{
   char *colorspec = gdk_rgba_to_string(color);
   
   msg_dbg ("colorspec: %s", colorspec);
   array_strPtr_replace_kill( ary, colorspec, index );
}


static void
ac_color_find_style_color( GtkWidget *widget, gchar *name, GdkRGBA *rgba)
{
   if ( ! name ) {
      name = (gchar *) gtk_widget_get_name (widget);
   }
   GtkStyleContext *scontext;
   scontext = gtk_widget_get_style_context (widget);
   if ( gtk_style_context_lookup_color(scontext, name, rgba) == 0) {
      msg_warning (_("Can't find color for '%s'"), name) ;
   }
}

/* 
 * color init from style or from rc
 */ 

void ac_color_rgba_init(GdkRGBA *destColor, GdkRGBA *styleColor, char *rcColor)
{
   int ret = 0;
   
   if ( rcColor && *rcColor ){
      ret = gdk_rgba_parse ( destColor, rcColor);
   } 
   
   if ( ret == 0 ) {
      msg_dbg("color == NULL using style color for (%s)", rcColor );
      if (styleColor) {
         memcpy( destColor, styleColor, sizeof(GdkRGBA) );
      }
   }
}

void ac_color_background_set ( UserData  *ud)
{
   ac_color_rgba_str_set( &ud->up->panelBgColor, ud->bg_color );
}

void ac_color_grid_set (UserData  *ud)
{
   ac_color_rgba_str_set( &ud->up->gridColor, ud->pg_color );
}

void ac_color_panel_grid_set (WavePanel *wp, gpointer data)
{
   GdkRGBA *color = (GdkRGBA *) data;
 
   if ( color ) {
      memcpy( wp->grid_color, color, sizeof(GdkRGBA) );
   }
}

/*
 * called in drawing configure once for each panel
 */
void ac_color_panel_grid_init (WavePanel *wp)
{
   wp->grid_color = g_new0 (GdkRGBA, 1);
   ac_color_panel_grid_set (wp, wp->ud->pg_color);
}


void ac_color_cursor_set ( UserData  *ud, int i )
{
   AWCursor *csp = ud->cursors[i];

   ac_color_rgba_ary_set( ud->up->cursorsColor, csp->color, i );
}

void ac_color_hl_set ( UserData  *ud )
{
   ac_color_rgba_str_set( &ud->up->hlColor, ud->hl_color );
}

void ac_color_srange_set ( UserData  *ud )
{
   ac_color_rgba_str_set( &ud->up->srangeColor, ud->srange->color );
}
void ac_color_bg_wave_button_set (VisibleWave *vw )
{
   GdkRGBA *color = vw->wp->ud->bg_color;
return;   
   gtk_widget_override_background_color (vw->button, GTK_STATE_NORMAL, color);
   gtk_widget_override_background_color (vw->button, GTK_STATE_PRELIGHT, color);
   gtk_widget_override_background_color (vw->button, GTK_STATE_ACTIVE, color);
}

void ac_color_wave_set (VisibleWave *vw)
{
   gtk_widget_override_color (vw->label, GTK_STATE_NORMAL, vw->color);
   gtk_widget_override_color (vw->label, GTK_STATE_PRELIGHT, vw->color);
   gtk_widget_override_color (vw->label, GTK_STATE_ACTIVE, vw->color);
   ac_color_bg_wave_button_set (vw );
}

void ac_color_wave_init (VisibleWave *vw, GdkRGBA *color)
{
   vw->color = g_new0 (GdkRGBA, 1);
   if ( color ) {
      memcpy( vw->color, color, sizeof(GdkRGBA) );
   } else {
      ac_color_find_style_color( vw->label, NULL, vw->color);
   }
   ac_color_wave_set (vw);
}

/*
 * initialize some vars from font settings once at startup
 */
void ac_color_font_init (WavePanel *wp)
{
   UserData *ud = wp->ud;
   PangoContext *context;
   PangoFontDescription *desc;
   PangoFont *font;
   PangoFontMetrics *metrics;

   context = gtk_widget_get_pango_context (wp->drawing);
   desc = pango_context_get_font_description ( context );

  /* FIXME - Should get the locale language here */
   pango_context_set_language (context, gtk_get_default_language());
   font = pango_context_load_font (context, desc);
   metrics = pango_font_get_metrics (font, pango_context_get_language (context));

   ud->char_width = 1 +
      PANGO_PIXELS (pango_font_metrics_get_approximate_char_width (metrics));
   ud->char_height =
      PANGO_PIXELS (pango_font_metrics_get_ascent (metrics)) +
      PANGO_PIXELS (pango_font_metrics_get_descent (metrics)) ;

   const char *family_name;
   family_name = pango_font_description_get_family(desc);

   ud->panelfont = app_strdup(family_name);
   msg_dbg("family '%s' char_width %d, char_height %d",
           family_name, ud->char_width, ud->char_height );
}

/*
 * initialize colors once at startup
 */
void ac_color_initialize (WavePanel *wp)
{
   UserData *ud = wp->ud;
   UserPrefs *up = ud->up;
   GdkRGBA styleColor;
   AWCursor *csp;
   int i;

   ud->bg_color = g_new0 (GdkRGBA, 1);
   /* background color */
   ac_color_find_style_color( wp->drawing, "da-bg", &styleColor);
   ac_color_rgba_init( ud->bg_color, &styleColor, up->panelBgColor );
   ac_color_background_set (ud);

   /* init bg for all created drawing */
   g_list_foreach(ud->panelList, (GFunc) pa_panel_drawing_background_set, NULL );
   
   /* graticule */
   ud->pg_color = g_new0 (GdkRGBA, 1);
   ac_color_find_style_color( wp->drawing, "graticule", &styleColor);
   ac_color_rgba_init( ud->pg_color, &styleColor, up->gridColor );
   ac_color_grid_set (ud);
   
   /* vertical bar cursors */
   for (i = 0 ; i < 2 ; i++) {
      char rcname[64];
      char *cursorColor = array_strPtr_get( up->cursorsColor, i);
      csp = ud->cursors[i];
      sprintf(rcname, "dacursor%d", i);

      csp->color = g_new0 (GdkRGBA, 1);
      ac_color_find_style_color( wp->drawing, rcname, &styleColor);
      ac_color_rgba_init( csp->color , &styleColor, cursorColor );
      ac_color_cursor_set (ud, i);
   }

   /* highlight */
   ud->hl_color = g_new0 (GdkRGBA, 1);
   ac_color_find_style_color( wp->drawing, "highlight", &styleColor);
   ac_color_rgba_init( ud->hl_color, &styleColor, up->hlColor );
   ac_color_hl_set (ud);

   /* select range */
   ud->srange->color = g_new0 (GdkRGBA, 1);
   ac_color_find_style_color( wp->drawing, "srange", &styleColor);
   ac_color_rgba_init( ud->srange->color, &styleColor, up->srangeColor );
   ac_color_srange_set (ud);

   ac_color_font_init (wp);
}


static gint
ac_color_dialog (GtkWidget *window, GdkRGBA *color, gchar *title )
{
   GtkWidget *dialog;
   gint response;

   dialog = gtk_color_chooser_dialog_new (title, GTK_WINDOW (window));
   
   gtk_window_set_transient_for (GTK_WINDOW (dialog), GTK_WINDOW (window));
  
   gtk_color_chooser_set_rgba (GTK_COLOR_CHOOSER(dialog), color);
  
   response = gtk_dialog_run (GTK_DIALOG (dialog));
   gtk_color_chooser_get_rgba (GTK_COLOR_CHOOSER(dialog), color);

   gtk_widget_destroy (dialog);

   return response;
}

void
ac_bp_color_wave_gaction (GSimpleAction *action, GVariant *param, gpointer user_data )
{
   VisibleWave *vw =  (VisibleWave *) user_data;
   UserData *ud = vw->wdata->ud;
   gint response;

   response = ac_color_dialog( ud->window, vw->color, _("Changing wave color"));
  
   if (response == GTK_RESPONSE_OK) {
      ac_color_wave_set(vw);
  
      pa_panel_full_redraw(vw->wp);
   }
}

void ac_pop_color_grid_gaction (GSimpleAction *action, GVariant *param, gpointer user_data )
{
   WavePanel *wp = (WavePanel *) user_data;
   gint response;
   
   if ( ! wp ) {
      return;
   }
   response = ac_color_dialog( wp->ud->window, wp->grid_color, _("Changing grid color"));
   
   if (response == GTK_RESPONSE_OK) {
      ac_color_panel_grid_set (wp, NULL);

      da_drawing_redraw(wp->drawing);
   }
}


int ac_color_background_cmd (UserData *ud, char *colorspec )
{
   if ( ! gdk_rgba_parse(ud->bg_color, colorspec) ) {
      return -1;
   }
   ac_color_background_set (ud);
   g_list_foreach(ud->panelList, (GFunc) pa_panel_drawing_background_set, NULL );
   ap_all_redraw(ud);
   return 0;
}

int ac_color_grid_cmd (UserData *ud, char *colorspec )
{
   if ( ! gdk_rgba_parse(ud->pg_color, colorspec) ) {
      return -1;
   }
   ac_color_grid_set (ud);
   g_list_foreach(ud->panelList, (GFunc) ac_color_panel_grid_set, ud->pg_color );
   ap_all_redraw(ud);
   return 0;
}

void ac_color_set_cb (GtkColorButton *widget, gpointer user_data)
{
   msg_dbg("dialog color cb");
   GdkRGBA *color = (GdkRGBA *) user_data;
   gtk_color_chooser_get_rgba(GTK_COLOR_CHOOSER(widget), color);
}

void
ac_color_panel_colors_gaction (GSimpleAction *action, GVariant *param, gpointer user_data )
{
   UserData *ud = (UserData *) user_data;
   GtkWidget *dialog;
   GtkWidget *vbox;
   GtkWidget *frame;
   GtkWidget *table;
   GtkWidget *label;
   GtkWidget *picker;
   GdkRGBA *color;
   gint response;
   
   dialog = gtk_dialog_new_with_buttons (_("Gaw panel colors settings"),
                                         GTK_WINDOW (ud->window),
                                         GTK_DIALOG_MODAL | GTK_DIALOG_DESTROY_WITH_PARENT,
                                         _("_OK"),
                                         GTK_RESPONSE_ACCEPT,
                                         _("_Cancel"),
                                         GTK_RESPONSE_REJECT,
                                         NULL);

   vbox = gtk_dialog_get_content_area (GTK_DIALOG (dialog));
   gtk_container_set_border_width (GTK_CONTAINER (vbox), 8);
   
   /* frame panel colors */
   frame = gtk_frame_new ( _("Panel Colors Settings"));
   gtk_box_pack_start (GTK_BOX (vbox), frame, FALSE, TRUE, 0);
   gtk_container_set_border_width (GTK_CONTAINER (frame), 8);

   table = gtk_grid_new ();    
   gtk_grid_set_column_spacing( GTK_GRID(table), 10);
   gtk_grid_set_row_spacing( GTK_GRID (table), 3);
   gtk_container_add (GTK_CONTAINER (frame), table);
   gtk_container_set_border_width (GTK_CONTAINER (table), 10);

   label = gtk_label_new (_("Background Color:"));
//   gtk_misc_set_alignment (GTK_MISC (label), 0.0, 0.5);
   gtk_widget_set_valign ( GTK_WIDGET (label), 0.5); 
//   gtk_label_set_yalign ( label, 0.5);

   color = ud->bg_color;
   picker =  gtk_color_button_new_with_rgba (color);
   gtk_grid_attach(GTK_GRID(table),  label, 
                /* left,    top,  width,   height    */
                      0,      0,      1,        1  );   
   gtk_grid_attach(GTK_GRID(table),  picker, 
                /* left,    top,  width,   height    */
                      1,      0,      1,        1  );   
   g_signal_connect (picker, "color-set",
                     G_CALLBACK (ac_color_set_cb), (gpointer) color );
      
   label = gtk_label_new (_("Grid Color:") );
//   gtk_misc_set_alignment (GTK_MISC (label), 0.0, 0.5);
   gtk_widget_set_valign ( GTK_WIDGET (label), 0.5); 
//   gtk_label_set_yalign ( label, 0.5);
   color = ud->pg_color;
   picker =  gtk_color_button_new_with_rgba (color);
   gtk_grid_attach(GTK_GRID(table),  label, 
                /* left,    top,  width,   height    */
                      0,      1,      1,        1  );   
   gtk_grid_attach(GTK_GRID(table),  picker, 
                /* left,    top,  width,   height    */
                      1,      1,      1,        1  );   
   g_signal_connect (picker, "color-set",
                     G_CALLBACK (ac_color_set_cb), (gpointer) color );

   label = gtk_label_new (_("Highlight Color:") );
//   gtk_misc_set_alignment (GTK_MISC (label), 0.0, 0.5);
   gtk_widget_set_valign ( GTK_WIDGET (label), 0.5); 
//   gtk_label_set_yalign ( label, 0.5);
   color = ud->hl_color;
   picker =  gtk_color_button_new_with_rgba (color);
   gtk_grid_attach(GTK_GRID(table),  label, 
                /* left,    top,  width,   height    */
                      0,      2,      1,        1  );   
   gtk_grid_attach(GTK_GRID(table),  picker, 
                /* left,    top,  width,   height    */
                      1,      2,      1,        1  );   
   g_signal_connect (picker, "color-set",
                     G_CALLBACK (ac_color_set_cb), (gpointer) color );

   label = gtk_label_new (_("Select Range Color:") );
//   gtk_misc_set_alignment (GTK_MISC (label), 0.0, 0.5);
   gtk_widget_set_valign ( GTK_WIDGET (label), 0.5); 
//   gtk_label_set_yalign ( label, 0.5);
   color = ud->srange->color;
   picker =  gtk_color_button_new_with_rgba (color);
   gtk_grid_attach(GTK_GRID(table),  label, 
                /* left,    top,  width,   height    */
                      0,      3,      1,        1  );   
   gtk_grid_attach(GTK_GRID(table),  picker, 
                /* left,    top,  width,   height    */
                      1,      3,      1,        1  );   
   g_signal_connect (picker, "color-set",
                     G_CALLBACK (ac_color_set_cb), (gpointer) color );

   label = gtk_label_new (_("Cursor 0 Color:") );
//   gtk_misc_set_alignment (GTK_MISC (label), 0.0, 0.5);
   gtk_widget_set_valign ( GTK_WIDGET (label), 0.5); 
//   gtk_label_set_yalign ( label, 0.5);
   color = ud->cursors[0]->color;
   picker =  gtk_color_button_new_with_rgba (color);
   gtk_grid_attach(GTK_GRID(table),  label, 
                /* left,    top,  width,   height    */
                      0,      4,      1,        1  );   
   gtk_grid_attach(GTK_GRID(table),  picker, 
                /* left,    top,  width,   height    */
                      1,      4,      1,        1  );   
   g_signal_connect (picker, "color-set",
                     G_CALLBACK (ac_color_set_cb), (gpointer) color );

   label = gtk_label_new (_("Cursor 1 Color:") );
//   gtk_misc_set_alignment (GTK_MISC (label), 0.0, 0.5);
   gtk_widget_set_valign ( GTK_WIDGET (label), 0.5); 
//   gtk_label_set_yalign ( label, 0.5);
   color = ud->cursors[1]->color;
   picker =  gtk_color_button_new_with_rgba (color);
   gtk_grid_attach(GTK_GRID(table),  label, 
                /* left,    top,  width,   height    */
                      0,      5,      1,        1  );   
   gtk_grid_attach(GTK_GRID(table),  picker, 
                /* left,    top,  width,   height    */
                      1,      5,      1,        1  );   
   g_signal_connect (picker, "color-set",
                     G_CALLBACK (ac_color_set_cb), (gpointer) color );

   gtk_widget_show_all (vbox);
   response = gtk_dialog_run (GTK_DIALOG (dialog));

  if (response == GTK_RESPONSE_ACCEPT) {
     msg_dbg("dialog OK");
     ac_color_background_set (ud);
     g_list_foreach(ud->panelList, (GFunc) pa_panel_background_set, NULL );
    /* init grid for all created drawing */
     g_list_foreach(ud->panelList, (GFunc) ac_color_panel_grid_set, ud->pg_color );
     ac_color_grid_set (ud);
     ac_color_cursor_set ( ud, 0 );
     ac_color_cursor_set ( ud, 1 );
     ac_color_hl_set ( ud );     
     ac_color_srange_set ( ud );     
     ap_all_redraw(ud);
  }

  gtk_widget_destroy (dialog);
}
