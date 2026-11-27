from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

NAMA_CAFE = "CAFE HOMESCHOOLING ANAK PELANGI"

MENU = {
    "ESP": ("Espresso", 15000),
    "AMR": ("Americano", 18000),
    "LAT": ("Caffe Latte", 22000),
    "CAP": ("Cappuccino", 22000),
    "CAR": ("Caramel Macchiato", 26000),
    "MOC": ("Mochaccino", 24000),
    "MAT": ("Matcha Latte", 25000),
    "CHO": ("Chocolate", 22000),
    "TAR": ("Taro Latte", 23000),
    "LEM": ("Lemon Tea", 16000),
}


def rp(n):
    return "Rp" + f"{n:,}".replace(",", ".")


def rincian(cart):
    baris = []
    for kode, jumlah in cart.items():
        nama, harga = MENU[kode]
        baris.append(f"- {nama} ({jumlah} pesanan x {rp(harga)}) = {rp(harga * jumlah)}")
    return "\n".join(baris)


def hitung(cart):
    total_item = sum(cart.values())
    total = sum(MENU[k][1] * j for k, j in cart.items())
    return total_item, total


def label_teks(**kw):
    """Label rata kiri yang tingginya mengikuti isi teks."""
    lb = Label(halign="left", valign="top", size_hint_y=None, **kw)
    lb.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
    lb.bind(texture_size=lambda i, s: setattr(i, "height", s[1] + 10))
    return lb


# ---------------- Layar 1: Identitas ----------------
class IdentitasScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=20, spacing=12)
        root.add_widget(Label(text=f"SISTEM KASIR\n{NAMA_CAFE}", font_size="20sp",
                              halign="center", size_hint_y=None, height=90))
        self.kasir = TextInput(hint_text="Nama Kasir", multiline=False,
                               size_hint_y=None, height=50)
        self.pelanggan = TextInput(hint_text="Nama Pelanggan", multiline=False,
                                   size_hint_y=None, height=50)
        self.catatan = TextInput(hint_text="Catatan Khusus Pelanggan (opsional)",
                                 multiline=False, size_hint_y=None, height=50)
        self.pesan = Label(text="", color=(1, 0.3, 0.3, 1), size_hint_y=None, height=30)
        btn = Button(text="LANJUT KE MENU", size_hint_y=None, height=60)
        btn.bind(on_press=self.lanjut)
        for w in (self.kasir, self.pelanggan, self.catatan, self.pesan, btn):
            root.add_widget(w)
        root.add_widget(Label())  # pengisi ruang
        self.add_widget(root)

    def lanjut(self, *_):
        app = App.get_running_app()
        if not self.kasir.text.strip() or not self.pelanggan.text.strip():
            self.pesan.text = "Nama kasir dan pelanggan wajib diisi!"
            return
        app.kasir = self.kasir.text.strip().title()
        app.pelanggan = self.pelanggan.text.strip().title()
        catatan = self.catatan.text.strip().capitalize()
        app.catatan = catatan if catatan else "Tidak ada catatan khusus."
        self.pesan.text = ""
        self.manager.current = "menu"

    def reset(self):
        self.kasir.text = ""
        self.pelanggan.text = ""
        self.catatan.text = ""


# ---------------- Layar 2: Menu ----------------
class MenuScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)
        root.add_widget(Label(text="DAFTAR MENU (ketuk untuk menambah 1)",
                              size_hint_y=None, height=35))

        grid = GridLayout(cols=2, spacing=8, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for kode, (nama, harga) in MENU.items():
            b = Button(text=f"{nama}\n{rp(harga)}", size_hint_y=None, height=70,
                       halign="center")
            b.bind(on_press=lambda _, k=kode: self.tambah(k))
            grid.add_widget(b)
        sv = ScrollView(size_hint_y=0.5)
        sv.add_widget(grid)
        root.add_widget(sv)

        root.add_widget(Label(text="PESANAN SAAT INI", size_hint_y=None, height=30))
        self.rincian = label_teks(text="")
        sv2 = ScrollView(size_hint_y=0.25)
        sv2.add_widget(self.rincian)
        root.add_widget(sv2)

        self.total = Label(text="", size_hint_y=None, height=35)
        root.add_widget(self.total)
        self.pesan = Label(text="", color=(1, 0.3, 0.3, 1), size_hint_y=None, height=25)
        root.add_widget(self.pesan)

        baris = BoxLayout(size_hint_y=None, height=55, spacing=8)
        b_undo = Button(text="Hapus Terakhir")
        b_undo.bind(on_press=self.hapus_terakhir)
        b_bayar = Button(text="BAYAR")
        b_bayar.bind(on_press=self.bayar)
        baris.add_widget(b_undo)
        baris.add_widget(b_bayar)
        root.add_widget(baris)
        self.add_widget(root)

    def on_pre_enter(self, *_):
        self.refresh()

    def tambah(self, kode):
        app = App.get_running_app()
        app.cart[kode] = app.cart.get(kode, 0) + 1
        app.urutan.append(kode)
        self.pesan.text = ""
        self.refresh()

    def hapus_terakhir(self, *_):
        app = App.get_running_app()
        if app.urutan:
            kode = app.urutan.pop()
            app.cart[kode] -= 1
            if app.cart[kode] == 0:
                del app.cart[kode]
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        self.rincian.text = rincian(app.cart) if app.cart else "(belum ada pesanan)"
        item, total = hitung(app.cart)
        self.total.text = f"Total Item: {item}   |   TOTAL: {rp(total)}"

    def bayar(self, *_):
        app = App.get_running_app()
        if not app.cart:
            self.pesan.text = "Belum ada menu yang dipesan!"
            return
        self.manager.current = "bayar"


# ---------------- Layar 3: Pembayaran ----------------
class BayarScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=15, spacing=10)
        root.add_widget(Label(text="RINGKASAN PESANAN SEBELUM PEMBAYARAN",
                              size_hint_y=None, height=35))
        self.ringkasan = label_teks(text="")
        sv = ScrollView()
        sv.add_widget(self.ringkasan)
        root.add_widget(sv)

        self.uang = TextInput(hint_text="Nominal uang bayar (angka saja)",
                              multiline=False, input_filter="int",
                              size_hint_y=None, height=50)
        self.pesan = Label(text="", color=(1, 0.3, 0.3, 1), size_hint_y=None, height=30)
        b_proses = Button(text="PROSES PEMBAYARAN", size_hint_y=None, height=60)
        b_proses.bind(on_press=self.proses)
        b_kembali = Button(text="Kembali ke Menu", size_hint_y=None, height=50)
        b_kembali.bind(on_press=lambda *_: setattr(self.manager, "current", "menu"))
        for w in (self.uang, self.pesan, b_proses, b_kembali):
            root.add_widget(w)
        self.add_widget(root)

    def on_pre_enter(self, *_):
        app = App.get_running_app()
        item, total = hitung(app.cart)
        self.ringkasan.text = (
            f"Pelanggan : {app.pelanggan}\n"
            f"Catatan   : {app.catatan}\n"
            f"{'-' * 30}\n"
            f"{rincian(app.cart)}\n"
            f"{'-' * 30}\n"
            f"Total Item    : {item} pesanan\n"
            f"TOTAL TAGIHAN : {rp(total)}"
        )
        self.uang.text = ""
        self.pesan.text = ""

    def proses(self, *_):
        app = App.get_running_app()
        _, total = hitung(app.cart)
        try:
            uang = int(self.uang.text)
        except ValueError:
            self.pesan.text = "Masukkan nominal uang bayar berupa angka!"
            return
        if uang < total:
            self.pesan.text = f"Uang bayar kurang {rp(total - uang)}!"
            return
        app.uang_bayar = uang
        self.manager.current = "struk"


# ---------------- Layar 4: Struk ----------------
class StrukScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=15, spacing=10)
        self.struk = label_teks(text="")
        sv = ScrollView()
        sv.add_widget(self.struk)
        root.add_widget(sv)
        b_baru = Button(text="TRANSAKSI BARU", size_hint_y=None, height=60)
        b_baru.bind(on_press=self.baru)
        root.add_widget(b_baru)
        self.add_widget(root)

    def on_pre_enter(self, *_):
        app = App.get_running_app()
        item, total = hitung(app.cart)
        kembalian = app.uang_bayar - total
        self.struk.text = (
            f"{NAMA_CAFE}\n"
            f"STRUK PEMBAYARAN\n"
            f"{'=' * 30}\n"
            f"Kasir          : {app.kasir}\n"
            f"Pelanggan      : {app.pelanggan}\n"
            f"Catatan Khusus : {app.catatan}\n"
            f"{'-' * 30}\n"
            f"DETAIL PESANAN:\n"
            f"{rincian(app.cart)}\n"
            f"{'-' * 30}\n"
            f"Total Pesanan  : {item} pesanan\n"
            f"Total Tagihan  : {rp(total)}\n"
            f"Uang Bayar     : {rp(app.uang_bayar)}\n"
            f"Uang Kembalian : {rp(kembalian)}\n"
            f"{'=' * 30}\n"
            f"Terima Kasih Telah Berkunjung ke Cafe Kami!"
        )

    def baru(self, *_):
        app = App.get_running_app()
        app.cart.clear()
        app.urutan.clear()
        self.manager.get_screen("identitas").reset()
        self.manager.current = "identitas"


# ---------------- Aplikasi ----------------
class KasirApp(App):
    def build(self):
        self.title = "Kasir Anak Pelangi"
        self.kasir = ""
        self.pelanggan = ""
        self.catatan = ""
        self.uang_bayar = 0
        self.cart = {}
        self.urutan = []
        sm = ScreenManager()
        sm.add_widget(IdentitasScreen(name="identitas"))
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(BayarScreen(name="bayar"))
        sm.add_widget(StrukScreen(name="struk"))
        return sm


if __name__ == "__main__":
    KasirApp().run()
