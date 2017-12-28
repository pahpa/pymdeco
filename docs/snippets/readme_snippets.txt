>>> from pymdeco import services
>>> srv = services.FileMetadataService()
>>> meta = srv.get_metadata('/tests/big_buck_bunny_720p_surround.avi')
>>> print(meta.to_json(indent=2)) # to pretty print the metadata
{
  "file_name": "big_buck_bunny_720p_surround.avi", 
  "file_type": "video", 
  "file_size": 332243668, 
  "mime_type": "video/x-msvideo", 
  "file_hash": {
    "value": "b957d6e6212638441b52d3b620af157cc8d40c2a0342669294854a06edcd528c", 
    "algorithm": "sha256"
  }, 
  "file_timestamps": {
    "modified": "2008-06-11 13:29:26", 
    "created": "2008-06-11 13:29:26"
  }, 
  "video_metadata": {
    "streams": [
      {
        "sample_aspect_ratio": "1:1", 
        "codec_type": "video", 
        "codec_name": "mpeg4", 
        "duration": "596.457", 
        "nb_frames": "14315", 
        "codec_time_base": "1/24", 
        "index": 0, 
        "width": 1280, 
        "divx_packed": "0", 
        "pix_fmt": "yuv420p", 
        "r_frame_rate": "24/1", 
        "start_time": "0.000", 
        "time_base": "208333/5000000", 
        "codec_tag_string": "FMP4", 
        "codec_long_name": "MPEG-4 part 2", 
        "display_aspect_ratio": "16:9", 
        "codec_tag": "0x34504d46", 
        "quarter_sample": "0", 
        "height": 720, 
        "avg_frame_rate": "0/0", 
        "level": 1, 
        "has_b_frames": 0
      }, 
      {
        "ltrt_cmixlev": "-1.000000", 
        "sample_fmt": "s16", 
        "bits_per_sample": 0, 
        "codec_type": "audio", 
        "channels": 6, 
        "codec_name": "ac3", 
        "loro_cmixlev": "-1.000000", 
        "loro_surmixlev": "-1.000000", 
        "nb_frames": "33402880", 
        "codec_time_base": "0/1", 
        "index": 1, 
        "r_frame_rate": "0/0", 
        "tags": {
          "title": "BBB-Master"
        }, 
        "dmix_mode": "-1", 
        "start_time": "0.000", 
        "time_base": "1/56000", 
        "codec_tag_string": "[0] [0][0]", 
        "codec_long_name": "ATSC A/52A (AC-3)", 
        "codec_tag": "0x2000", 
        "ltrt_surmixlev": "-1.000000", 
        "avg_frame_rate": "125/4", 
        "sample_rate": "48000"
      }
    ], 
    "format": {
      "tags": {
        "JUNK": "", 
        "encoder": "AVI-Mux GUI 1.17.7, Aug  8 2006  20:59:17"
      }, 
      "nb_streams": 2, 
      "start_time": "0.000", 
      "format_long_name": "AVI format", 
      "format_name": "avi", 
      "filename": "/tests/big_buck_bunny_720p_surround.avi", 
      "bit_rate": "4456226", 
      "duration": "596.457", 
      "size": "332243668"
    }
  }
}
>>> 
>>> meta = srv.get_metadata('/tests/jonobacon-freesoftwaresong2.mp3')
>>> print(meta.to_json(indent=2)) # to pretty print the metadata
{
  "file_name": "jonobacon-freesoftwaresong2.mp3", 
  "file_type": "audio", 
  "file_size": 3169160, 
  "mime_type": "audio/mpeg", 
  "file_hash": {
    "value": "d7ebc161d5d8fb802659fea949204af2958906b91913ca7577cfaeece90ffb78", 
    "algorithm": "sha256"
  }, 
  "file_timestamps": {
    "modified": "2012-01-09 20:02:23", 
    "created": "2012-01-09 20:02:23"
  }, 
  "audio_metadata": {
    "streams": [
      {
        "index": 0, 
        "sample_fmt": "s16", 
        "codec_tag": "0x0000", 
        "bits_per_sample": 0, 
        "r_frame_rate": "0/0", 
        "start_time": "0.000", 
        "time_base": "1/14112000", 
        "codec_tag_string": "[0][0][0][0]", 
        "codec_type": "audio", 
        "channels": 2, 
        "codec_long_name": "MP3 (MPEG audio layer 3)", 
        "codec_name": "mp3", 
        "duration": "198.034", 
        "sample_rate": "44100", 
        "codec_time_base": "0/1", 
        "avg_frame_rate": "1225/32"
      }
    ], 
    "format": {
      "tags": {
        "album": "Released as a single", 
        "artist": "Jono Bacon", 
        "track": "1", 
        "title": "Free Software Song 2", 
        "date": "2011", 
        "genre": "Metal"
      }, 
      "nb_streams": 1, 
      "start_time": "0.000", 
      "format_long_name": "MPEG audio layer 2/3", 
      "format_name": "mp3", 
      "filename": "/tests/jonobacon-freesoftwaresong2.mp3", 
      "bit_rate": "128024", 
      "duration": "198.034", 
      "size": "3169160"
    }
  }
}
>>> 
>>> meta = srv.get_metadata('/tests/some_image.jpg')
>>> print(meta.to_json(indent=2)) # to pretty print the metadata
{
  "file_name": "some_image.jpg", 
  "file_type": "image", 
  "file_size": 159894, 
  "mime_type": "image/jpeg", 
  "file_hash": {
    "value": "844a8750f2c9e1a24175c8f158abb6d204ec2b79fc49aba512cded3cdb3a0111", 
    "algorithm": "sha256"
  }, 
  "file_timestamps": {
    "modified": "2012-01-09 20:43:12", 
    "created": "2012-01-09 20:43:12"
  }, 
  "image_metadata": {
    "Exif": {
      "Photo": {
        "LightSource": 0, 
        "PixelXDimension": 900, 
        "SubSecTime": "16", 
        "ExposureMode": 0, 
        "Flash": 0, 
        "SceneCaptureType": 0, 
        "MeteringMode": 5, 
        "ExposureBiasValue": 0, 
        "Contrast": 0, 
        "ExposureProgram": 3, 
        "FocalLengthIn35mmFilm": 200, 
        "SubSecTimeOriginal": "16", 
        "ColorSpace": 1, 
        "PixelYDimension": 599, 
        "DateTimeDigitized": "2008-09-13 11:26:41", 
        "DateTimeOriginal": "2008-09-13 11:26:41", 
        "UserComment": "                                    ", 
        "SubSecTimeDigitized": "16", 
        "SubjectDistanceRange": 0, 
        "WhiteBalance": 0, 
        "SensingMethod": 2, 
        "FNumber": "7/2", 
        "CustomRendered": 0, 
        "FocalLength": 200, 
        "Saturation": 0, 
        "ISOSpeedRatings": 200, 
        "ExposureTime": "1/3200", 
        "MaxApertureValue": 3, 
        "Sharpness": 0, 
        "GainControl": 0, 
        "DigitalZoomRatio": 1
      }, 
      "Image": {
        "YResolution": 72, 
        "ResolutionUnit": 2, 
        "Orientation": 1, 
        "Copyright": "Some Rights Reserved                                  ", 
        "Artist": "Yovko Lambrev                       ", 
        "Make": "NIKON CORPORATION", 
        "DateTime": "2008-09-13 11:26:41", 
        "ExifTag": 334, 
        "PhotometricInterpretation": 32803, 
        "XResolution": 72, 
        "Model": "NIKON D700", 
        "Software": "Aperture 3.2.2"
      }
    }, 
    "Xmp": {
      "iptc": {
        "CreatorContactInfo/Iptc4xmpCore:CiEmailWork": "yovko@simplestudio.org", 
        "CreatorContactInfo/Iptc4xmpCore:CiAdrCity": "Sofia", 
        "CreatorContactInfo/Iptc4xmpCore:CiUrlWork": "http://simplestudio.org", 
        "CreatorContactInfo/Iptc4xmpCore:CiAdrCtry": "Bulgaria"
      }, 
      "photoshop": {
        "City": "Golden Sands", 
        "AuthorsPosition": "Photographer", 
        "Country": "Bulgaria"
      }, 
      "aux": {
        "Lens": "AF-S VR Zoom-Nikkor 70-200mm f/2.8G IF-ED", 
        "ImageNumber": "248", 
        "SerialNumber": "2032686", 
        "LensID": "606370574", 
        "FlashCompensation": "0/1"
      }, 
      "dc": {
        "creator": "[u'Yovko Lambrev']", 
        "rights": "{u'x-default': u'Yovko Lambrev'}"
      }, 
      "xmpRights": {
        "UsageTerms": "{u'x-default': u'You are free to use, copy, share and distribute this photo under the terms of Creative Commons Attribution-NonCommercial license.'}"
      }
    }, 
    "Iptc": {
      "Application2": {
        "CountryName": "['Bulgaria']", 
        "Byline": "['Yovko Lambrev']", 
        "BylineTitle": "['Photographer']", 
        "Copyright": "['Yovko Lambrev']", 
        "City": "['Golden Sands']", 
        "RecordVersion": "[2]"
      }, 
      "Envelope": {
        "CharacterSet": "['\\x1b%G']"
      }
    }
  }
}
>>> 
>>> meta = srv.get_metadata('/tests/minimal_ubuntu_11.04_natty.iso')
>>> print(meta.to_json(indent=2)) # to pretty print the metadata
{
  "file_name": "minimal_ubuntu_11.04_natty.iso", 
  "file_type": "application", 
  "file_size": 19922944, 
  "mime_type": "application/x-iso9660-image", 
  "file_hash": {
    "value": "8607e2c06090db13b06a216efbeb65d7aeff4ca8666904e6874cf4a5960f2366", 
    "algorithm": "sha256"
  }, 
  "file_timestamps": {
    "modified": "2011-05-02 17:24:18", 
    "created": "2011-05-02 17:24:18"
  }
}
>>> 