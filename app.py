import os
import threading
import customtkinter
import tkinter
import libtorrent as lt


class DownloadWindow:
    def __init__(self, master):
        self.master = master
        master.title("Torrent Downloader")
        master.geometry("400x200")

        self.link_label = tkinter.Label(master, text="Magnet Link:")
        self.link_label.pack(pady=(20, 5))

        self.link_entry = tkinter.Entry(master, width=50)
        self.link_entry.pack(pady=5)

        self.start_button = tkinter.Button(
            master, text="Start Download", command=self.start_download)
        self.start_button.pack(pady=10)

        self.progress_label = tkinter.Label(master, text="")
        self.progress_label.pack(pady=5)

        self.complete_label = tkinter.Label(master, text="")
        self.complete_label.pack(pady=(5, 20))

        self.complete_label = tkinter.Label(master, text="")
        self.complete_label.pack()

    def start_download(self):
        self.start_button.config(state=tkinter.DISABLED)
        link = self.link_entry.get()
        threading.Thread(target=self.download_torrent, args=(link,)).start()

    def download_torrent(self, link):
        # Create a session object
        ses = lt.session()

        # Add a torrent to the session from a magnet link
        params = {"save_path": "."}
        handle = lt.add_magnet_uri(ses, link, params)

        # Start downloading the torrent
        self.progress_label.config(text="Downloading metadata...")
        while not handle.has_metadata():
            continue

        self.progress_label.config(text="Starting torrent download...")
        ses.start_dht()
        ses.start_lsd()
        ses.start_upnp()
        ses.start_natpmp()
        while handle.status().state != lt.torrent_status.seeding:
            s = handle.status()
            state_str = ['queued', 'checking', 'downloading metadata',
                         'downloading', 'finished', 'seeding', 'allocating']
            progress_str = '%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % \
                (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000,
                 s.num_peers, state_str[s.state])
            self.progress_label.config(text=progress_str)
            if s.state == lt.torrent_status.error:
                print(handle.status().error)
                break

        # Save the downloaded file
        if handle.status().state == lt.torrent_status.seeding:
            torinfo = handle.get_torrent_info()
            torfile = lt.create_torrent(torinfo)
            with open(os.path.join(params['save_path'], torinfo.name() + ".torrent"), "wb") as f:
                f.write(lt.bencode(torfile.generate()))
            self.progress_label.config(text="Download complete.")
            self.complete_label.config(text="Download complete.")
        self.start_button.config(state=tkinter.NORMAL)


root = tkinter.Tk()
app = DownloadWindow(root)
root.mainloop()
