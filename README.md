# 360 Stitcher — Version 5

Developed by Ahmad Alhasanat

## Windows launch

Extract the ZIP to a new folder and double-click `Start_Mavic360_Windows.bat`.
The first run requires Python 3 (with Tkinter) and internet to install the image-processing libraries. Later launches reuse them.

1. Choose a folder containing one capture's individual JPG/TIFF/PNG photos and DJI metadata CSV.
2. Select the output filename and format: JPG, PNG or TIFF.
3. Choose 4000 × 2000 (preview), 8000 × 4000 (high), or 12000 × 6000 (ultra).
4. Click **Stitch panorama**, then **Open 360 viewer**.
5. Drag to look around and use the mouse wheel to zoom.

For a standalone Windows executable, run `Build_Windows_EXE.bat` on Windows with Python and internet available. It creates `dist\360Stitcher.exe`, including the logo and application icon. The executable build has not been tested in the Linux development environment.

## Quality improvements

- Robust feature alignment refines DJI camera rotations and lens focal length.
- Source detail scales with output resolution, up to original size.
- Lanczos image resampling preserves fine detail during spherical projection.
- JPG exports at quality 98 with no chroma subsampling; PNG and TIFF use lossless compression. All output remains 8-bit RGB.
- The viewer uses bilinear interpolation and retains up to 8192 × 4096 texture detail.
- Processing uses strips to reduce temporary memory. Ultra mode still needs considerably more RAM; use High or Preview if memory is limited.
- An adjacent `.alignment.json` file records matching and alignment results.

The supplied logo appears in the interface, application window icon and Windows executable icon. It is packaged as supplied; its checkerboard is part of the JPEG, not transparency. The exact credit “Developed by Ahmad Alhasanat” appears in the main app and viewer. The exported panorama contains the scene without a watermark.

## Input and completeness

DJI CSV mode creates a 2:1 equirectangular panorama. Without a compatible CSV, the fallback creates a general panorama, which may not be suitable for the 360 viewer. DNG/RAW requires conversion to JPG or TIFF first.

The available SD-TA-RM-001 test capture includes 22 of 25 listed photos. PANO0014.JPG, PANO0018.JPG and PANO0025.JPG were not supplied in that ZIP. Missing shots and the unphotographed upper sky remain black. This app does not synthesize missing views. Higher resolution cannot recover missing coverage, remove every parallax effect, or guarantee a perfect sphere.

## Command line

`python stitch.py CAPTURE_FOLDER -o panorama.jpg --max-edge 4000`

For DJI CSV captures, output width equals twice `--max-edge`; 4000 produces 8000 × 4000. The GUI uses explicit resolution presets instead.

Photos are processed locally on your computer.

## GitHub publishing

The repository includes GitHub Actions to build a standalone Windows executable on every push to `main` and attach it to a release when a version tag (`v1.0.0`, for example) is pushed. The download page in `docs/` deploys with GitHub Pages. In repository Settings → Pages, choose **GitHub Actions** as the build source. The release download stays on GitHub; no source photos or sample panorama are committed.

After publishing the repository, push a version tag to create the first downloadable release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Check the Windows app workflow and its release asset before sharing the Pages URL. The app remains a Windows desktop program; GitHub Pages serves its download page.
