# Rename browser tab title from Mammas bilder to Bildgalleri

Now that the gallery can serve dpfas_media as well as momfiles, "Mammas bilder" ("Mom's pictures")
undersold what's actually shown. Joakim's call, confirmed via AskUserQuestion: "Bildgalleri" ("Photo
gallery") over the alternatives (DPFAS - an English acronym meaningless to Elisabeth; "Familjens
bilder") to stay consistent with the rest of the UI's Swedish and be meaningful to both accounts.
Single-line change (`app/static/index.html`'s `<title>`), no test depended on the old text.

- **Doc size**: no other docs touched this entry.
