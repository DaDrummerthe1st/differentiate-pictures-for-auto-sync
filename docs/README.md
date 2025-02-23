***This application has several purposes***

Since Google started to add all pictures to the Google One quota thus limiting the possibilities to take pictures and later delete the ones you can discard I decided to create my own project handling pictures and movie clips so the user itself owns the information and also the metadata.

*The overall idea is handling pictures and movies in order to preserve and being able to find old, forgotten ones. At the same time categorising them for future AI to do it automatically, set for each users individual preferences.*



## List of features
- Sort / delete files

    *Possibility to delete, sort, flag and even mark custom objects within a picture or a movie clip*
- Recognise and follow above pattern for each individual user by the use of an AI
- Sync and save all picture in a secure manner 
- Shared syncing

    *For better reliability the user share some of its disk space with the network (choose globally or a set of friends). In return the user get space on the internet for some of its files through their respective shared space. All done in a safe manner, only the people the user choose shall have access to chosen files.*



## External sources
To help up with this project I am thinking about implementing the following open source applications:

| Project name | Project site | Description | Implemented? |
| ------ | ------ | ------ | ------ |
| LabelImg | https://github.com/tzutalin/labelImg | labelling pictures | 🔴 |
| SyncThing | https://syncthing.net/ | continuously syncing between units | 🔴 |
| rClone | https://blog.rymcg.tech/blog/linux/rclone_sync/ | auto sync of files for bash | 🔴 |



## The work order as for now is:
1. Handle pictures
*Create an overview on a PC screen to label files for deletion, save and sort.
Implement labelling*
2. Syncing between devices
3. Syncing from an Android phone to a local computer using local WLAN
4. Syncing from an Android phone to a local computer using WAN
