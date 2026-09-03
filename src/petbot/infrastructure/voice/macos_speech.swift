import AVFoundation
import Foundation
import Speech

let locale = Locale(identifier: CommandLine.arguments.dropFirst().first ?? "es-ES")
let outputPath = CommandLine.arguments.dropFirst(2).first
let recognizer = SFSpeechRecognizer(locale: locale)!
let authorization = DispatchSemaphore(value: 0)
var authorized = false
SFSpeechRecognizer.requestAuthorization { status in
    authorized = status == .authorized
    if !authorized { fputs("Reconocimiento de voz no autorizado (estado: \(status.rawValue)).\n", stderr) }
    authorization.signal()
}
authorization.wait()
if !authorized { exit(1) }
if !recognizer.isAvailable { fputs("El reconocimiento de voz no está disponible ahora mismo.\n", stderr); exit(1) }

let request = SFSpeechAudioBufferRecognitionRequest()
request.shouldReportPartialResults = false
request.taskHint = .dictation
let engine = AVAudioEngine()
let input = engine.inputNode
let format = input.outputFormat(forBus: 0)
input.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in request.append(buffer) }
engine.prepare()
do { try engine.start() } catch { fputs("No se pudo abrir el micrófono.\n", stderr); exit(1) }

// La activación es manual: escucha una frase y cierra el audio tras ocho segundos.
DispatchQueue.main.asyncAfter(deadline: .now() + 8) {
    request.endAudio()
    engine.stop()
    input.removeTap(onBus: 0)
}

let task = recognizer.recognitionTask(with: request) { result, error in
    if let result = result, result.isFinal {
        let transcription = result.bestTranscription.formattedString
        if let outputPath = outputPath { try? transcription.write(toFile: outputPath, atomically: true, encoding: .utf8) }
        print(transcription)
        request.endAudio(); engine.stop(); input.removeTap(onBus: 0); exit(0)
    }
    if let error = error {
        fputs("Error de reconocimiento: \(error.localizedDescription)\n", stderr)
        request.endAudio(); engine.stop(); input.removeTap(onBus: 0); exit(1)
    }
}
RunLoop.main.run()
_ = task
