import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { documents } from '../services/api'

export default function UploadPage() {
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return
    setUploading(true)
    setMessage('')
    try {
      const res = await documents.upload(file)
      setMessage(`Uploaded: ${res.data.filename} (ID: ${res.data.id})`)
    } catch (err: any) {
      setMessage(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: false,
  })

  return (
    <div className="card">
      <h2>Upload Clinical Document</h2>
      <div {...getRootProps()} className="dropzone">
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the PDF here...</p>
        ) : (
          <p>Drag & drop a PDF file here, or click to select one</p>
        )}
      </div>
      {uploading && <p style={{ marginTop: 12 }}>Uploading...</p>}
      {message && (
        <p style={{ marginTop: 12, color: message.startsWith('Uploaded') ? '#065f46' : '#b91c1c' }}>
          {message}
        </p>
      )}
    </div>
  )
}
