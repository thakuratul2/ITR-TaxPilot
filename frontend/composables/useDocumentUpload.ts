export const useDocumentUpload = () => {
  const isUploading = useState<boolean>('doc_uploading', () => false)
  const currentStep = useState<number>('doc_step', () => 1)
  const isResultsVisible = useState<boolean>('doc_results_visible', () => false)
  const uploadError = useState<string | null>('doc_upload_error', () => null)

  const {
    grossSalary,
    allowancesSec10,
    professionalTax,
    tdsDeducted,
    assessmentYear,
    deduction80C,
    deduction80D,
    deductionNPS,
    deductionHomeLoan,
  } = useTaxCalculator()

  const { currentUser, authToken, openAuthModal } = useAuth()

  const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

  const processForm16File = async (file?: File) => {
    isUploading.value = true
    isResultsVisible.value = false
    uploadError.value = null
    currentStep.value = 1

    let extracted: any = null

    // Parallel extraction promise
    const extractPromise = (async () => {
      if (file) {
        const formData = new FormData()
        formData.append('file', file)
        try {
          const res = await fetch('/api/v1/documents/form16', {
            method: 'POST',
            headers: authToken.value ? { Authorization: `Bearer ${authToken.value}` } : {},
            body: formData,
          })
          if (res.ok) {
            const json = await res.json()
            if (json.data && json.data.extracted) {
              return json.data.extracted
            }
          }
        } catch (e) {
          console.warn('Backend extraction error:', e)
        }
      }
      return null
    })()

    // Step 1: Security scan
    await sleep(600)
    currentStep.value = 2

    // Step 2: PyMuPDF Text & Table Extraction
    await sleep(700)
    currentStep.value = 3

    // Step 3: AI Normalization
    extracted = await extractPromise
    await sleep(600)
    currentStep.value = 4

    // Step 4: Apply real values to reactive state
    if (file && extracted) {
      grossSalary.value = extracted.gross_salary || 0
      tdsDeducted.value = extracted.total_tds_deducted || 0
      professionalTax.value = extracted.professional_tax_sec16iii || 0
      allowancesSec10.value = extracted.exempt_allowances_sec10 || 0
      assessmentYear.value = extracted.assessment_year || '2026-27'

      let ext80c = 0
      let ext80d = 0
      if (extracted.deductions_chapter_vi_a) {
        for (const d of extracted.deductions_chapter_vi_a) {
          if (d.section === '80C') ext80c = d.amount || 0
          if (d.section === '80D') ext80d = d.amount || 0
        }
      }
      deduction80C.value = ext80c
      deduction80D.value = ext80d
      deductionNPS.value = 0
      deductionHomeLoan.value = 0
    } else if (!file) {
      // Sample Demo Data (₹26.06 Lakh)
      grossSalary.value = 2606700
      allowancesSec10.value = 0
      professionalTax.value = 2500
      tdsDeducted.value = 299630
      assessmentYear.value = '2026-27'
      deduction80C.value = 150000
      deduction80D.value = 25000
      deductionNPS.value = 50000
      deductionHomeLoan.value = 0
    }

    await sleep(500)
    isUploading.value = false

    if (currentUser.value) {
      isResultsVisible.value = true
    } else {
      openAuthModal(false, true)
    }
  }

  const unlockResults = () => {
    isResultsVisible.value = true
  }

  return {
    isUploading,
    currentStep,
    isResultsVisible,
    uploadError,
    processForm16File,
    unlockResults,
  }
}
