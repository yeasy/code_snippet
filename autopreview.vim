" Description:
"   Vim plugin for previewing definitions of variables or functions on
"   the cursor automatically like Source Insight, it's great conveniet
"   when insight source codes.
"
" Maintainer: Yang Baohua <yangbaohua[At]gmail.com>
" Last Change: 2008 July 29
" Version: v1.0
"
" Acknowledgements:
"   Thanks to Vim-help & Mail-list
"   thinelephant[At]newsmth
"   Dieken[At]newsmth
"
" Usage:
"   Drop this file to your plugin directory of vim.
"
"   Set g:AutoPreview_enabled to 1 or 0 and g:AutoPreview_allowed_filetypes
"   in your vimrc, here is the default setting:
"
"     let g:AutoPreview_enabled = 1
"     let g:AutoPreview_allowed_filetypes = ["c", "cpp", "java"]
"
"   The file type of current buffer can be checked with `:echo &ft`, and
"   you can call `:AutoPreviewToggle` command to enable or disable this
"   plugin at runtime, for example:
"
"     nnoremap <F5> :AutoPreviewToggle<CR> 
"     inoremap <F5> <ESC>:AutoPreviewToggle<CR>i 
"
"   You'd better set 'updatetime' option to 1000 or even less for good
"   responsibility, see `:help updatetime` for details, for example:
"
"     set updatetime=500
"
" ChangeLog:
"   2008-05-07  Yang Baohua <yangbaohua@gmail.com>
"     release v0.1
"       * initial inspiration and implementation
"
"   2008-05-09  Liu Yubao <yubao.liu@gmail.com>
"     release v0.2
"       * cleanup, optimize and enhance
"
"   2008-07-29  Yang Baohua <yangbaohua@gmail.com>
"     release v1.0: a stable and total version
"       * add highlight effect with previewword
"       * deal with folded codes
"       * some changes with the use guide document

if exists ("loaded_autopreview") || !has("autocmd") || !exists(":filetype")
    finish
endif
let loaded_autopreview = 1


if !exists("g:AutoPreview_enabled")
    let g:AutoPreview_enabled = 0
endif
if !exists("g:AutoPreview_allowed_filetypes")
    let g:AutoPreview_allowed_filetypes = ["c", "cpp", "java"]
endif

command! -nargs=0 -bar AutoPreviewToggle :call s:AutoPreviewToggle()

if g:AutoPreview_enabled
    augroup AutoPreview
        au! FileType * :call s:SetCursorHoldAutoCmd()
    augroup END
endif


func s:AutoPreviewToggle()
    if g:AutoPreview_enabled
        silent! exe "pclose"
        silent! :au! AutoPreview
    else 
        silent! call s:PreviewWord()
        augroup AutoPreview
            au! FileType * :call s:SetCursorHoldAutoCmd()
            let i = 1
            let n = bufnr("$")
            while (i <= n)
                if buflisted(i) && index(g:AutoPreview_allowed_filetypes,
                            \            getbufvar(i, "&ft")) >= 0 &&
                            \   !getbufvar(i, "&previewwindow")
                    exe "au! CursorHold <buffer=" . i . "> nested :call s:PreviewWord()"
                    exe "au! CursorHoldI <buffer=" . i . "> nested :call s:PreviewWord()"
                endif
                let i = i + 1
            endwhile
        augroup END
    endif
    let g:AutoPreview_enabled = !g:AutoPreview_enabled
endfunc


func s:SetCursorHoldAutoCmd()
    if &previewwindow
        return
    endif

    augroup AutoPreview
        if index(g:AutoPreview_allowed_filetypes, &ft) >= 0
            " auto refresh the ptag window
            au! CursorHold <buffer> nested :call s:PreviewWord()
            au! CursorHoldI <buffer> nested :call s:PreviewWord()
            ":echo "set autocmd for " . &ft . " in " . expand("%")
        else
            au! CursorHold <buffer>
            au! CursorHoldI <buffer>
            ":echo "unset autocmd for " . &ft . " in " . expand("%")
        endif
    augroup END
endfunc

func s:PreviewWord()
    if &previewwindow
        return
    endif
    let w = expand("<cword>")     " get the word under cursor
    if w =~ '\a'                  " if the word contains a letter
        try
            silent! exe "ptag " . w
        catch
            return
        endtry
        let oldwin = winnr() "get current window
        silent! wincmd P "jump to preview window 
        if &previewwindow "if jump to preview windows successfully
            if has("folding")
                silent! .foldopen "unfold
            endif
            call search("$","b") "to the end of last line
            let w = substitute(w,'\\','\\\\',"")
            call search('\<\V' . w . '\>') "cursor on the match word

            match none "delete the current highlight marks

            "high light the match word in the previewwindow
            hi previewWord term=bold ctermbg=green guibg=green
            exe 'match previewWord "\%' . line(".") . 'l\%' . col(".") . 'c\k*"'
            exec oldwin.'wincmd w'  
            "back from preview window
        endif
    endif
endfun

