export function formatError(error) {
  if (error.response) {
    const status = error.response.status
    const data = error.response.data

    if (data?.detail) {
      return data.detail
    }

    switch (status) {
      case 400:
        return 'Invalid data provided'
      case 401:
        return 'Unauthorized - check your credentials'
      case 403:
        return 'Access denied - insufficient permissions'
      case 404:
        return 'Resource not found'
      case 422:
        return 'Invalid input data'
      case 500:
        return 'Internal server error'
      case 502:
        return 'Server temporarily unavailable'
      case 503:
        return 'Service temporarily unavailable'
      default:
        return `Server error (${status})`
    }
  } else if (error.request) {
    return 'Connection error - check your internet'
  } else if (error.code) {
    switch (error.code) {
      case 'ENOENT':
        return 'File or directory not found'
      case 'EACCES':
        return 'Permission denied to access the file'
      case 'ENOTDIR':
        return 'Specified path is not a directory'
      case 'TIMEOUT':
        return 'Operation timed out - try again'
      default:
        return error.message || 'Unknown error'
    }
  }

  return error.message || 'Unknown error'
}

export function formatFileError(error) {
  if (error.code) {
    switch (error.code) {
      case 'ENOENT':
        return 'File or folder not found'
      case 'EACCES':
        return 'No permission to access this location'
      case 'ENOTDIR':
        return 'The path is not a valid folder'
      case 'EISDIR':
        return 'The path is a folder, not a file'
      case 'EMFILE':
      case 'ENFILE':
        return 'Too many open files - try again'
      case 'ENOSPC':
        return 'Insufficient disk space'
      default:
        return `File error: ${error.message}`
    }
  }

  return formatError(error)
}

export function isRetryableError(error) {
  if (error.request && !error.response) {
    return true
  }

  if (error.response) {
    const status = error.response.status
    return status >= 500 || status === 408 || status === 429
  }

  if (error.code) {
    const retryableCodes = ['EMFILE', 'ENFILE', 'EAGAIN', 'EBUSY']
    return retryableCodes.includes(error.code)
  }

  return false
}

export function getErrorSeverity(error) {
  if (error.response) {
    const status = error.response.status
    if (status >= 500) return 'critical'
    if (status === 404 || status === 403) return 'high'
    if (status >= 400) return 'medium'
  }

  if (error.request && !error.response) {
    return 'high'
  }

  if (error.code) {
    const criticalCodes = ['ENOSPC', 'EACCES']
    if (criticalCodes.includes(error.code)) return 'critical'

    const highCodes = ['ENOENT', 'ENOTDIR']
    if (highCodes.includes(error.code)) return 'high'
  }

  return 'medium'
}
