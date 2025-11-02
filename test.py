""" def debug_list_MEIPASS():
            if hasattr(sys, '_MEIPASS'):
                base = sys._MEIPASS
            else:
                base = abspath(".")

            with open("log.txt", "w", encoding="utf-8") as f:
                f.write(f"BASE PATH: {base}\n")
                f.write("FILES in BASE:\n")

                for item in listdir(base):
                    f.write(f" - {item}\n")

                # se existir images
                images_path = join(base, "images")
                if exists(images_path):
                    f.write("\nFILES in images:\n")
                    for item in listdir(images_path):
                        f.write(f" - {item}\n")
                else:
                    f.write("\n(images folder not found)\n")"""