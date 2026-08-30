export interface TaxRegimeResult {
  grossIncome: number
  stdDeduction: number
  totalDeductions?: number
  taxableIncome: number
  baseTax: number
  rebate87a: number
  cess: number
  totalTax: number
  effectiveRate: number
  netPayableOrRefund: number
}

export const useTaxCalculator = () => {
  const grossSalary = useState<number>('tax_gross_salary', () => 0)
  const allowancesSec10 = useState<number>('tax_allowances_sec10', () => 0)
  const professionalTax = useState<number>('tax_professional_tax', () => 0)
  const tdsDeducted = useState<number>('tax_tds_deducted', () => 0)
  const assessmentYear = useState<string>('tax_ay', () => '2026-27')

  // Reactive Deduction Sliders
  const deduction80C = useState<number>('tax_ded_80c', () => 0)
  const deduction80D = useState<number>('tax_ded_80d', () => 0)
  const deductionNPS = useState<number>('tax_ded_nps', () => 0)
  const deductionHomeLoan = useState<number>('tax_ded_home_loan', () => 0)

  // Computed New Tax Regime
  const newRegimeResult = computed<TaxRegimeResult>(() => {
    const stdDeduction = 75000
    const taxableIncome = Math.max(0, grossSalary.value - allowancesSec10.value - stdDeduction)

    let tax = 0
    if (taxableIncome > 1500000) {
      tax += (taxableIncome - 1500000) * 0.30
      tax += 300000 * 0.20
      tax += 200000 * 0.15
      tax += 300000 * 0.10
      tax += 400000 * 0.05
    } else if (taxableIncome > 1200000) {
      tax += (taxableIncome - 1200000) * 0.20
      tax += 200000 * 0.15
      tax += 300000 * 0.10
      tax += 400000 * 0.05
    } else if (taxableIncome > 1000000) {
      tax += (taxableIncome - 1000000) * 0.15
      tax += 300000 * 0.10
      tax += 400000 * 0.05
    } else if (taxableIncome > 700000) {
      tax += (taxableIncome - 700000) * 0.10
      tax += 400000 * 0.05
    } else if (taxableIncome > 300000) {
      tax += (taxableIncome - 300000) * 0.05
    }

    // Section 87A Rebate & Marginal Relief
    let rebate87a = 0
    if (taxableIncome <= 700000) {
      rebate87a = tax
      tax = 0
    } else if (taxableIncome <= 727777) {
      const excessIncome = taxableIncome - 700000
      if (tax > excessIncome) {
        rebate87a = tax - excessIncome
        tax = excessIncome
      }
    }

    const cess = Math.round(tax * 0.04)
    const totalTax = Math.round(tax + cess)
    const net = totalTax - tdsDeducted.value
    const effectiveRate = grossSalary.value > 0 ? (totalTax / grossSalary.value) * 100 : 0

    return {
      grossIncome: grossSalary.value,
      stdDeduction,
      taxableIncome,
      baseTax: Math.round(tax),
      rebate87a: Math.round(rebate87a),
      cess,
      totalTax,
      effectiveRate,
      netPayableOrRefund: net,
    }
  })

  // Computed Old Tax Regime
  const oldRegimeResult = computed<TaxRegimeResult>(() => {
    const stdDeduction = 50000
    const totalDeductions =
      deduction80C.value +
      deduction80D.value +
      deductionNPS.value +
      deductionHomeLoan.value +
      professionalTax.value

    const taxableIncome = Math.max(0, grossSalary.value - allowancesSec10.value - stdDeduction - totalDeductions)

    let tax = 0
    if (taxableIncome > 1000000) {
      tax += (taxableIncome - 1000000) * 0.30
      tax += 500000 * 0.20
      tax += 250000 * 0.05
    } else if (taxableIncome > 500000) {
      tax += (taxableIncome - 500000) * 0.20
      tax += 250000 * 0.05
    } else if (taxableIncome > 250000) {
      tax += (taxableIncome - 250000) * 0.05
    }

    let rebate87a = 0
    if (taxableIncome <= 500000) {
      rebate87a = Math.min(tax, 12500)
      tax = Math.max(0, tax - rebate87a)
    }

    const cess = Math.round(tax * 0.04)
    const totalTax = Math.round(tax + cess)
    const net = totalTax - tdsDeducted.value
    const effectiveRate = grossSalary.value > 0 ? (totalTax / grossSalary.value) * 100 : 0

    return {
      grossIncome: grossSalary.value,
      stdDeduction,
      totalDeductions,
      taxableIncome,
      baseTax: Math.round(tax),
      rebate87a: Math.round(rebate87a),
      cess,
      totalTax,
      effectiveRate,
      netPayableOrRefund: net,
    }
  })

  const isNewRegimeRecommended = computed(() => {
    return newRegimeResult.value.totalTax <= oldRegimeResult.value.totalTax
  })

  const savingsAmount = computed(() => {
    return Math.abs(oldRegimeResult.value.totalTax - newRegimeResult.value.totalTax)
  })

  const formatINR = (num: number) => {
    return '₹' + Math.round(num).toLocaleString('en-IN')
  }

  return {
    grossSalary,
    allowancesSec10,
    professionalTax,
    tdsDeducted,
    assessmentYear,
    deduction80C,
    deduction80D,
    deductionNPS,
    deductionHomeLoan,
    newRegimeResult,
    oldRegimeResult,
    isNewRegimeRecommended,
    savingsAmount,
    formatINR,
  }
}
