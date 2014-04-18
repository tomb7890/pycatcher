  ** TODO: replace ad-hoc with optparse **

  ** BUG: repro steps:
     1. delete an mp3
     2. delete corresonding links
     3. run script
     
  ** ERROR CONDITION:
    link isn't recreated for newly downloaded mp3 for deleted file
    Test peudocode:

   sub = Subscriptions.find("ffrf")
    episdoes = sub.eps()
    # delete number 2
    os.unlink (episodes[2].disk_file())

    # delete all links
    for e in episodes:
        os.unlikn( e.link()
    # run main program
    self.assertEqual for 3 programs, 3 linnks.

