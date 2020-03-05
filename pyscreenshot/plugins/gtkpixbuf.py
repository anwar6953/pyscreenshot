from pyscreenshot.plugins.backend import CBackend
from pyscreenshot.tempexport import read_func_img
import logging
import sys

log = logging.getLogger(__name__)

# based on:
# http://stackoverflow.com/questions/69645/take-a-screenshot-via-a-python-script-linux

PY2 = sys.version_info[0] == 2


class GtkError(Exception):
    pass


"""
>>> import gtk
>>> import gi
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/lib/python2.7/dist-packages/gi/__init__.py", line 39, in <module>
    raise ImportError(_static_binding_error)
ImportError: When using gi.repository you must not import static modules like "gobject". 
Please change all occurrences of "import gobject" to "from gi.repository import GObject". See: https://bugzilla.gnome.org/show_bug.cgi?id=709183
"""
# gdk3pixpuf can not be used after gtk was imported in the same process,
# so this module will be put in childprocess as gdk3pixpuf is more important.


class GtkPixbufWrapper(CBackend):
    name = "pygtk"
    childprocess = False
    apply_childprocess = True

    def __init__(self):
        # no pygtk for py3
        if not PY2:
            raise GtkError()

        import gtk

        self.gtk = gtk
        try:
            gtk.gdk.Pixbuf
            gtk.gdk.COLORSPACE_RGB
        except AttributeError as e:
            log.info(e)
            raise GtkError("Incompatible with Python3 / GDK3. Use gdk3pixbuf.")

    def grab(self, bbox=None):
        im = read_func_img(self._grab_to_file, bbox)
        return im

    def _grab_to_file(self, filename, bbox=None):
        """http://www.pygtk.org/docs/pygtk/class-gdkpixbuf.html.

        only "jpeg" or "png"
        """

        w = self.gtk.gdk.get_default_root_window()
        #       Capture the whole screen.
        if bbox is None:
            try:
                sz = w.get_size()
            except AttributeError:
                sz = (w.get_width(), w.get_height())
            try:
                pb = self.gtk.gdk.Pixbuf(
                    self.gtk.gdk.COLORSPACE_RGB, False, 8, sz[0], sz[1]
                )  # 24bit RGB
                pb = pb.get_from_drawable(w, w.get_colormap(), 0, 0, 0, 0, sz[0], sz[1])
            except TypeError:
                pb = self.gtk.gdk.pixbuf_get_from_window(w, 0, 0, sz[0], sz[1])
        #       Only capture what we need. The smaller the capture, the faster.
        else:
            sz = [bbox[2] - bbox[0], bbox[3] - bbox[1]]
            try:
                pb = self.gtk.gdk.Pixbuf(
                    self.gtk.gdk.COLORSPACE_RGB, False, 8, sz[0], sz[1]
                )
                pb = pb.get_from_drawable(
                    w, w.get_colormap(), bbox[0], bbox[1], 0, 0, sz[0], sz[1]
                )
            except TypeError:
                pb = self.gtk.gdk.pixbuf_get_from_window(
                    w, bbox[0], bbox[1], sz[0], sz[1]
                )
        assert pb
        ftype = "png"
        try:
            pb.save(filename, ftype)
        except AttributeError:
            pb.savev(filename, ftype, [], ())

    def backend_version(self):
        return ".".join(map(str, self.gtk.ver))
