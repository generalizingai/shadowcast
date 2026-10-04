// Subject cutout using Apple Vision (macOS 14+): cutout <in.jpg|png> <out.png>
// Writes a transparent PNG of the foreground subject, cropped to its bounds with a small margin.
import AppKit
import CoreImage
import Vision

let args = CommandLine.arguments
guard args.count == 3, let src = CIImage(contentsOf: URL(fileURLWithPath: args[1])) else {
  FileHandle.standardError.write("usage: cutout <in> <out.png>\n".data(using: .utf8)!); exit(1)
}
let handler = VNImageRequestHandler(ciImage: src)
let req = VNGenerateForegroundInstanceMaskRequest()
do { try handler.perform([req]) } catch { FileHandle.standardError.write("vision failed: \(error)\n".data(using: .utf8)!); exit(2) }
guard let obs = req.results?.first, !obs.allInstances.isEmpty else {
  FileHandle.standardError.write("no subject found\n".data(using: .utf8)!); exit(3)
}
let buf = try obs.generateMaskedImage(ofInstances: obs.allInstances, from: handler, croppedToInstancesExtent: true)
let out = CIImage(cvPixelBuffer: buf)
let ctx = CIContext()
guard let cg = ctx.createCGImage(out, from: out.extent) else { exit(4) }
let rep = NSBitmapImageRep(cgImage: cg)
guard let png = rep.representation(using: .png, properties: [:]) else { exit(5) }
try png.write(to: URL(fileURLWithPath: args[2]))
print("ok \(cg.width)x\(cg.height)")
